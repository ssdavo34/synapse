"""
OpenAI API 통합 클라이언트
==========================

목적:
    - OpenAI API 호출을 위한 통합 래퍼 클래스
    - 재시도 로직 (네트워크 오류, Rate Limit 대응)
    - 에러 처리 및 로깅
    - 모든 에이전트에서 공통으로 사용

특징:
    - 비동기 지원 (async/await)
    - tenacity를 사용한 자동 재시도 (최대 3회)
    - 지수 백오프 (exponential backoff)
    - 구조화된 에러 로깅

사용법:
    from backend.services.openai_client import OpenAIClient

    client = OpenAIClient()
    response = await client.chat_completion(
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.7
    )
    print(response.choices[0].message.content)
"""

import openai
from typing import List, Dict, Any, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from utils.logger import setup_logger


class OpenAIClient:
    """
    OpenAI API 클라이언트 래퍼

    모든 에이전트가 LLM을 호출할 때 이 클래스를 사용합니다.
    재시도 로직과 에러 처리를 중앙화하여 일관성을 보장합니다.

    Attributes:
        client (openai.AsyncOpenAI): OpenAI 비동기 클라이언트
        logger (logging.Logger): JSON 로거
        default_model (str): 기본 모델명
    """

    def __init__(self):
        """
        OpenAI 클라이언트 초기화

        설정에서 API 키와 기본 모델을 가져옵니다.
        비동기 클라이언트를 생성합니다.
        """
        # ============================================================
        # OpenAI 비동기 클라이언트 생성
        # ============================================================
        self.client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key
        )

        # ============================================================
        # 로거 설정
        # ============================================================
        self.logger = setup_logger("OpenAIClient")

        # ============================================================
        # 기본 모델 설정
        # ============================================================
        self.default_model = settings.default_model

        self.logger.info(
            "OpenAI client initialized",
            extra={"default_model": self.default_model}
        )

    @retry(
        # ============================================================
        # 재시도 설정 (tenacity)
        # ============================================================
        # 최대 3회 재시도
        stop=stop_after_attempt(3),

        # 지수 백오프: 2^x초 (1초, 2초, 4초 대기)
        # multiplier=1: 기본 배수
        # min=1: 최소 1초
        # max=10: 최대 10초
        wait=wait_exponential(multiplier=1, min=1, max=10),

        # 다음 예외 발생 시만 재시도
        retry=retry_if_exception_type((
            openai.RateLimitError,      # Rate Limit 초과
            openai.APIConnectionError,  # 네트워크 연결 오류
            openai.APITimeoutError,     # 타임아웃
        )),

        # 재시도 전 로그 출력
        before_sleep=before_sleep_log(
            logging.getLogger("OpenAIClient"),
            logging.WARNING
        )
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Any:
        """
        OpenAI Chat Completion API 호출

        Args:
            messages (List[Dict[str, str]]): 대화 메시지 리스트
                예: [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": "Hello"}
                ]

            model (Optional[str]): 사용할 모델명
                None이면 default_model 사용
                예: "gpt-4o-mini", "gpt-4o"

            temperature (float): 응답 창의성 (0.0~2.0)
                0에 가까울수록 결정적, 2에 가까울수록 창의적
                기본값: 0.7

            max_tokens (Optional[int]): 최대 토큰 수
                None이면 모델 기본값 사용

            response_format (Optional[Dict[str, str]]): 응답 포맷
                예: {"type": "json_object"} - JSON 출력 강제

            **kwargs: 추가 OpenAI API 파라미터
                top_p, frequency_penalty, presence_penalty 등

        Returns:
            Any: OpenAI API 응답 객체
                response.choices[0].message.content로 텍스트 접근

        Raises:
            openai.AuthenticationError: API 키 오류
            openai.BadRequestError: 잘못된 요청
            openai.RateLimitError: Rate Limit 초과 (재시도 후에도 실패)
            openai.APIError: 기타 API 오류

        Example:
            >>> client = OpenAIClient()
            >>> response = await client.chat_completion(
            ...     messages=[{"role": "user", "content": "Hello"}],
            ...     temperature=0.3
            ... )
            >>> print(response.choices[0].message.content)
            "Hello! How can I help you today?"
        """
        # ============================================================
        # 파라미터 준비
        # ============================================================
        # 모델: 지정되지 않으면 기본 모델 사용
        model = model or self.default_model

        # API 호출 파라미터 구성
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs  # 추가 파라미터
        }

        # max_tokens 설정 (지정된 경우만)
        if max_tokens is not None:
            params["max_tokens"] = max_tokens

        # response_format 설정 (JSON 모드 등)
        if response_format is not None:
            params["response_format"] = response_format

        # ============================================================
        # 로그: API 호출 시작
        # ============================================================
        self.logger.info(
            "Calling OpenAI API",
            extra={
                "model": model,
                "temperature": temperature,
                "message_count": len(messages),
                "response_format": response_format
            }
        )

        try:
            # ============================================================
            # OpenAI API 호출 (비동기)
            # ============================================================
            response = await self.client.chat.completions.create(**params)

            # ============================================================
            # 로그: API 호출 성공
            # ============================================================
            self.logger.info(
                "OpenAI API call successful",
                extra={
                    "model": model,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )

            return response

        except openai.AuthenticationError as e:
            # ============================================================
            # API 키 오류 (재시도 불가)
            # ============================================================
            self.logger.error(
                "OpenAI authentication failed",
                extra={"error": str(e)}
            )
            raise

        except openai.BadRequestError as e:
            # ============================================================
            # 잘못된 요청 (재시도 불가)
            # ============================================================
            self.logger.error(
                "Invalid request to OpenAI API",
                extra={"error": str(e), "model": model}
            )
            raise

        except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError) as e:
            # ============================================================
            # 재시도 가능한 에러 (tenacity가 자동 재시도)
            # ============================================================
            self.logger.warning(
                "OpenAI API error (will retry)",
                extra={"error_type": type(e).__name__, "error": str(e)}
            )
            raise  # tenacity가 재시도

        except openai.APIError as e:
            # ============================================================
            # 기타 API 오류
            # ============================================================
            self.logger.error(
                "OpenAI API error",
                extra={"error": str(e)}
            )
            raise

    async def count_tokens_estimate(self, text: str) -> int:
        """
        토큰 수 추정 (간단한 근사치)

        실제 프로젝트에서는 tiktoken 라이브러리 사용 권장

        Args:
            text (str): 토큰을 계산할 텍스트

        Returns:
            int: 토큰 수 (근사치)
        """
        # 4글자 ≈ 1토큰 (영어 기준)
        return len(text) // 4

    def create_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        동기 방식 간편 래퍼 (Synchronous wrapper)

        간단한 텍스트 완성 요청을 위한 동기 메서드입니다.
        내부적으로 asyncio를 사용하여 비동기 chat_completion을 호출합니다.

        Args:
            prompt: 프롬프트 텍스트
            model: 사용할 모델 (기본값: None, default_model 사용)
            temperature: 창의성 (0.0~2.0)
            max_tokens: 최대 토큰 수

        Returns:
            str: 응답 텍스트

        Examples:
            >>> client = OpenAIClient()
            >>> response = client.create_completion("Say hello in one word")
            >>> print(response)
            Hello!
        """
        import asyncio

        async def _async_call():
            response = await self.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        # 새 이벤트 루프에서 실행
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(_async_call())

    def get_model_info(self) -> Dict[str, Any]:
        """
        현재 설정된 모델 정보 반환

        Returns:
            Dict[str, Any]: 모델 정보
        """
        return {
            "default_model": self.default_model,
            "api_key_configured": bool(settings.openai_api_key)
        }


# ============================================================
# 테스트 코드 (python -m backend.services.openai_client 실행 시)
# ============================================================
if __name__ == "__main__":
    """OpenAI Client 동작 테스트"""

    import asyncio

    async def test_openai_client():
        """OpenAI Client 테스트"""

        print("=== OpenAI Client Test ===\n")

        # ============================================================
        # 1. 클라이언트 생성
        # ============================================================
        client = OpenAIClient()
        print(f"✅ Client initialized")
        print(f"   Default model: {client.default_model}\n")

        # ============================================================
        # 2. 간단한 Chat Completion 테스트
        # ============================================================
        print("🔄 Testing chat completion...")

        try:
            response = await client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello, World!' in Korean."}
                ],
                temperature=0.3,
                max_tokens=50
            )

            content = response.choices[0].message.content
            print(f"✅ Response: {content}")
            print(f"   Tokens used: {response.usage.total_tokens}\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")
            return

        # ============================================================
        # 3. JSON 모드 테스트
        # ============================================================
        print("🔄 Testing JSON mode...")

        try:
            response = await client.chat_completion(
                messages=[
                    {"role": "user", "content": 'Return a JSON object with keys "greeting" and "language". Greeting should be "Hello" and language should be "English".'}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            print(f"✅ JSON Response: {content}\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")

        # ============================================================
        # 4. 모델 정보 확인
        # ============================================================
        info = client.get_model_info()
        print(f"📊 Model Info: {info}")

    # ============================================================
    # asyncio 이벤트 루프 실행
    # ============================================================
    asyncio.run(test_openai_client())
