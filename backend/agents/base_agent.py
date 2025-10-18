"""
BaseAgent: 모든 에이전트의 추상 기반 클래스
============================================

목적:
    - 10개 전문 에이전트의 공통 인터페이스 및 기능 제공
    - 일관된 에이전트 동작 보장
    - 코드 재사용성 극대화

설계 원칙:
    1. 단일 책임: 각 에이전트는 하나의 핵심 기능만 담당
    2. 상태 무저장: 에이전트는 상태를 가지지 않음 (DB에 저장)
    3. 표준 인터페이스: execute() 메서드로 통일
    4. 느슨한 결합: 에이전트 간 직접 호출 금지 (OrchestratorAgent 경유)
    5. 확장 가능: 새 에이전트 추가 시 기존 코드 수정 최소화

사용법:
    class MyAgent(BaseAgent):
        async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
            self.validate_input(task, required_fields=["param1"])
            # 처리 로직
            return {"status": "success", "result": "data"}
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
from backend.utils.logger import setup_logger


class BaseAgent(ABC):
    """
    모든 에이전트의 추상 기반 클래스

    이 클래스를 상속받는 10개 에이전트:
        1. DocumentAgent: PDF 문서 처리
        2. SummaryAgent: 문서 요약 생성
        3. QuizAgent: 퀴즈 생성
        4. GradingAgent: 퀴즈 채점
        5. RAGAgent: 질문-답변 (RAG 기반)
        6. DiagnosisAgent: 학습자 진단
        7. PlanningAgent: 학습 계획 생성
        8. EvaluationAgent: 세션 평가
        9. RecommendationAgent: 자료 추천
        10. ConversationAgent: 대화 요약
        (11. OrchestratorAgent: 워크플로우 조율)

    Attributes:
        config (Dict[str, Any]): 에이전트 설정 딕셔너리
        logger (logging.Logger): JSON 로거
        _start_time (Optional[float]): 타이머 시작 시간
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        에이전트 초기화

        Args:
            config (Optional[Dict[str, Any]]): 에이전트 설정 딕셔너리
                예: {"model": "gpt-4o-mini", "temperature": 0.3}
                None이면 빈 딕셔너리 사용

        Example:
            >>> agent = DocumentAgent(config={"chunk_size": 500})
        """
        # ============================================================
        # 설정 저장 (None이면 빈 딕셔너리)
        # ============================================================
        self.config = config or {}

        # ============================================================
        # 로거 설정 (클래스명을 로거 이름으로 사용)
        # ============================================================
        # 예: DocumentAgent의 경우 로거 이름은 "DocumentAgent"
        self.logger = setup_logger(self.__class__.__name__)

        # ============================================================
        # 타이머 초기화 (성능 측정용)
        # ============================================================
        self._start_time: Optional[float] = None

        # ============================================================
        # 초기화 로그
        # ============================================================
        self.logger.info(f"{self.__class__.__name__} initialized")

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        에이전트 실행 (추상 메서드)

        모든 하위 클래스는 이 메서드를 **반드시 구현**해야 함
        이 메서드가 각 에이전트의 핵심 로직을 담당

        Args:
            task (Dict[str, Any]): 작업 정의 딕셔너리
                공통 필드:
                    - task_type (str): 작업 유형 (필수)
                에이전트별 추가 필드:
                    - DocumentAgent: file_path, session_id
                    - SummaryAgent: session_id, summary_type
                    - QuizAgent: session_id, num_questions
                    - RAGAgent: session_id, question
                    - 등등...

        Returns:
            Dict[str, Any]: 실행 결과 딕셔너리
                공통 필드:
                    - status (str): "success", "error", "no_answer"
                    - processing_time (float): 소요 시간 (초)
                에이전트별 추가 필드:
                    - DocumentAgent: chunks_count, embeddings_count
                    - SummaryAgent: summary, cache_hit
                    - QuizAgent: quiz_id, questions
                    - 등등...

        Raises:
            ValueError: 입력 검증 실패
            Exception: 실행 중 에러

        Example:
            >>> result = await agent.execute({
            ...     "task_type": "process_document",
            ...     "file_path": "data/uploads/doc.pdf",
            ...     "session_id": "abc-123"
            ... })
            >>> print(result["status"])  # "success"
        """
        pass  # 하위 클래스에서 구현

    def validate_input(self, task: Dict[str, Any], required_fields: list[str]) -> bool:
        """
        입력 검증 (공통 로직)

        task_type과 에이전트별 필수 필드를 검증합니다.

        Args:
            task (Dict[str, Any]): 검증할 작업 딕셔너리
            required_fields (list[str]): 추가 필수 필드 목록
                예: ["file_path", "session_id"]

        Returns:
            bool: 검증 성공 시 True

        Raises:
            ValueError: 필수 필드 누락 시 예외 발생

        Example:
            >>> self.validate_input(task, required_fields=["session_id"])
            True
        """
        # ============================================================
        # task_type 필드는 모든 에이전트에서 필수
        # ============================================================
        if "task_type" not in task:
            raise ValueError("task_type is required")

        # ============================================================
        # 에이전트별 추가 필수 필드 확인
        # ============================================================
        for field in required_fields:
            if field not in task:
                raise ValueError(f"Required field missing: {field}")

        # ============================================================
        # 검증 성공 로그
        # ============================================================
        self.logger.info(f"Input validation passed for task_type: {task['task_type']}")
        return True

    def _start_timer(self):
        """
        타이머 시작

        성능 측정을 위해 작업 시작 시간을 기록합니다.
        _calculate_time()과 함께 사용됩니다.

        Example:
            >>> self._start_timer()
            >>> # ... 작업 수행 ...
            >>> duration = self._calculate_time()
            >>> print(f"소요 시간: {duration}초")
        """
        self._start_time = time.time()

    def _calculate_time(self) -> float:
        """
        경과 시간 계산

        _start_timer() 호출 후 경과된 시간을 계산하고
        타이머를 리셋합니다.

        Returns:
            float: 경과 시간 (초, 소수점 둘째자리까지)
                   타이머가 시작되지 않았으면 0.0 반환

        Example:
            >>> self._start_timer()
            >>> time.sleep(1.5)
            >>> duration = self._calculate_time()
            >>> print(duration)  # 1.50
        """
        # ============================================================
        # 타이머가 시작되지 않았으면 0.0 반환
        # ============================================================
        if self._start_time is None:
            return 0.0

        # ============================================================
        # 경과 시간 계산 및 타이머 리셋
        # ============================================================
        elapsed = time.time() - self._start_time
        self._start_time = None  # 다음 호출을 위해 리셋
        return round(elapsed, 2)

    def _count_tokens(self, text: str) -> int:
        """
        토큰 수 계산 (근사치)

        LLM API 비용 추정 및 컨텍스트 관리에 사용됩니다.

        현재 구현:
            - 간단한 근사치: 4글자 ≈ 1 토큰
            - 실제 프로젝트에서는 tiktoken 사용 권장

        Args:
            text (str): 토큰을 계산할 텍스트

        Returns:
            int: 토큰 수 (근사치)

        Note:
            정확한 토큰 계산이 필요하면 다음과 같이 구현:
            ```python
            import tiktoken
            encoding = tiktoken.encoding_for_model("gpt-4o-mini")
            return len(encoding.encode(text))
            ```

        Example:
            >>> tokens = self._count_tokens("Hello, World!")
            >>> print(tokens)  # 3 (13글자 / 4)
        """
        # ============================================================
        # 간단한 근사: 4글자 = 1 토큰
        # ============================================================
        # 영어 기준으로는 대략 맞지만, 한글/일본어는 더 많은 토큰 소모
        # 정확도보다 빠른 추정이 목적
        return len(text) // 4

    def log_execution(
        self,
        task: Dict[str, Any],
        result: Dict[str, Any],
        duration: float
    ):
        """
        실행 결과 로깅

        에이전트 실행이 완료되면 결과를 JSON 로그로 기록합니다.

        Args:
            task (Dict[str, Any]): 입력 작업
            result (Dict[str, Any]): 실행 결과
            duration (float): 소요 시간 (초)

        Example:
            >>> self.log_execution(
            ...     task={"task_type": "summarize"},
            ...     result={"status": "success"},
            ...     duration=2.5
            ... )
            # 로그: {"task_type": "summarize", "status": "success",
            #       "duration_seconds": 2.5, "agent": "SummaryAgent"}
        """
        self.logger.info(
            f"Execution completed",
            extra={
                "task_type": task.get("task_type"),
                "status": result.get("status"),
                "duration_seconds": duration,
                "agent": self.__class__.__name__
            }
        )

    async def safe_execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        안전한 실행 래퍼 (에러 처리 포함)

        execute() 메서드를 호출하되, 모든 예외를 캐치하여
        일관된 에러 응답을 반환합니다.

        장점:
            - 에이전트 실행 중 예외가 발생해도 앱이 중단되지 않음
            - 에러를 로그로 기록하여 디버깅 용이
            - 일관된 에러 응답 포맷

        Args:
            task (Dict[str, Any]): 작업 딕셔너리

        Returns:
            Dict[str, Any]: 실행 결과
                성공 시: execute() 반환값
                실패 시: {
                    "status": "error",
                    "error_type": "validation_error" | "execution_error",
                    "error_message": "에러 메시지",
                    "processing_time": 소요 시간
                }

        Example:
            >>> result = await agent.safe_execute({
            ...     "task_type": "test",
            ...     "invalid_field": "value"
            ... })
            >>> if result["status"] == "error":
            ...     print(f"에러: {result['error_message']}")
        """
        # ============================================================
        # 타이머 시작
        # ============================================================
        self._start_timer()

        try:
            # ============================================================
            # 에이전트 실행 (하위 클래스의 execute() 호출)
            # ============================================================
            result = await self.execute(task)

            # ============================================================
            # 성공 시: 소요 시간 계산 및 로그
            # ============================================================
            duration = self._calculate_time()
            self.log_execution(task, result, duration)
            return result

        except ValueError as e:
            # ============================================================
            # 입력 검증 에러 (validate_input 실패)
            # ============================================================
            duration = self._calculate_time()
            self.logger.error(f"Validation error: {str(e)}")
            return {
                "status": "error",
                "error_type": "validation_error",
                "error_message": str(e),
                "processing_time": duration
            }

        except Exception as e:
            # ============================================================
            # 기타 실행 에러 (예상치 못한 예외)
            # ============================================================
            duration = self._calculate_time()
            # exc_info=True: 스택 트레이스 포함
            self.logger.error(f"Execution error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error_type": "execution_error",
                "error_message": str(e),
                "processing_time": duration
            }


# ============================================================
# 테스트 코드 (python -m backend.agents.base_agent 실행 시)
# ============================================================
if __name__ == "__main__":
    """BaseAgent 동작 테스트"""

    import asyncio

    # ============================================================
    # Mock 에이전트 정의 (테스트용)
    # ============================================================
    class MockAgent(BaseAgent):
        """테스트용 Mock 에이전트"""

        async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
            """Mock 실행"""
            # 1. 입력 검증
            self.validate_input(task, required_fields=["message"])

            # 2. Mock 처리
            message = task["message"]
            self.logger.info(f"Processing message: {message}")

            # 3. 토큰 계산 테스트
            token_count = self._count_tokens(message)

            # 4. 약간의 지연 (실제 작업 시뮬레이션)
            await asyncio.sleep(0.1)

            # 5. 결과 반환
            return {
                "status": "success",
                "message": f"Processed: {message}",
                "token_count": token_count
            }

    # ============================================================
    # 테스트 실행 함수
    # ============================================================
    async def test():
        """BaseAgent 테스트"""
        agent = MockAgent()

        # ============================================================
        # 테스트 1: 정상 케이스
        # ============================================================
        result1 = await agent.safe_execute({
            "task_type": "test",
            "message": "Hello, World!"
        })
        print("\n=== Test 1: Success Case ===")
        print(result1)

        # ============================================================
        # 테스트 2: 검증 실패 케이스 (message 필드 누락)
        # ============================================================
        result2 = await agent.safe_execute({
            "task_type": "test"
            # message 필드 누락
        })
        print("\n=== Test 2: Validation Error ===")
        print(result2)

        # ============================================================
        # 테스트 3: task_type 누락 케이스
        # ============================================================
        result3 = await agent.safe_execute({
            "message": "No task type"
        })
        print("\n=== Test 3: Missing task_type ===")
        print(result3)

    # ============================================================
    # asyncio 이벤트 루프 실행
    # ============================================================
    asyncio.run(test())
