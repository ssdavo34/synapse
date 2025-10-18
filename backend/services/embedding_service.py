"""
임베딩 서비스
=============

목적:
    - 텍스트를 벡터(임베딩)로 변환
    - DocumentAgent: 문서 청크 임베딩 (벡터 DB 저장용)
    - RAGAgent: 질문 임베딩 (유사도 검색용)

특징:
    - 단일/배치 처리 지원
    - OpenAI Embeddings API 사용
    - 모델: text-embedding-3-small (1536차원)
    - 효율적인 배치 처리

사용법:
    from backend.services.embedding_service import EmbeddingService

    service = EmbeddingService()

    # 단일 텍스트
    vector = await service.generate_embedding("텍스트")

    # 다중 텍스트 (배치)
    vectors = await service.generate_embeddings(["텍스트1", "텍스트2"])
"""

import openai
from typing import List
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

from backend.config import settings
from backend.utils.logger import setup_logger


class EmbeddingService:
    """
    임베딩 생성 서비스

    텍스트를 고차원 벡터로 변환하여 의미적 유사도 계산을 가능하게 합니다.

    사용 사례:
        - DocumentAgent: PDF 청크를 벡터로 변환하여 ChromaDB에 저장
        - RAGAgent: 사용자 질문을 벡터로 변환하여 유사 문서 검색

    Attributes:
        client (openai.AsyncOpenAI): OpenAI 비동기 클라이언트
        logger (logging.Logger): JSON 로거
        embedding_model (str): 임베딩 모델명
        embedding_dimension (int): 벡터 차원 (1536)
    """

    def __init__(self):
        """
        임베딩 서비스 초기화

        OpenAI 클라이언트를 생성하고 임베딩 모델을 설정합니다.
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
        self.logger = setup_logger("EmbeddingService")

        # ============================================================
        # 임베딩 모델 설정
        # ============================================================
        # text-embedding-3-small: 1536차원, 빠르고 비용 효율적
        # text-embedding-3-large: 3072차원, 더 정확하지만 비용↑
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536

        self.logger.info(
            "Embedding service initialized",
            extra={
                "model": self.embedding_model,
                "dimension": self.embedding_dimension
            }
        )

    @retry(
        # ============================================================
        # 재시도 설정 (OpenAIClient와 동일)
        # ============================================================
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
            openai.RateLimitError,
            openai.APIConnectionError,
            openai.APITimeoutError,
        )),
        before_sleep=before_sleep_log(
            logging.getLogger("EmbeddingService"),
            logging.WARNING
        )
    )
    async def generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        여러 텍스트의 임베딩 생성 (배치 처리)

        배치 처리를 통해 API 호출 횟수를 줄이고 효율성을 높입니다.

        Args:
            texts (List[str]): 임베딩을 생성할 텍스트 리스트
                예: ["텍스트1", "텍스트2", "텍스트3"]

        Returns:
            List[List[float]]: 임베딩 벡터 리스트
                각 벡터는 1536차원의 실수 리스트
                예: [[0.1, 0.2, ...], [0.3, 0.4, ...], ...]

        Raises:
            ValueError: 빈 리스트 또는 빈 텍스트 포함 시
            openai.APIError: OpenAI API 오류

        Example:
            >>> service = EmbeddingService()
            >>> vectors = await service.generate_embeddings([
            ...     "토마토는 빨갛다",
            ...     "하늘은 파랗다"
            ... ])
            >>> len(vectors)
            2
            >>> len(vectors[0])
            1536
        """
        # ============================================================
        # 입력 검증
        # ============================================================
        if not texts:
            raise ValueError("texts list cannot be empty")

        if any(not text.strip() for text in texts):
            raise ValueError("texts cannot contain empty strings")

        # ============================================================
        # 로그: 임베딩 생성 시작
        # ============================================================
        self.logger.info(
            "Generating embeddings",
            extra={
                "text_count": len(texts),
                "model": self.embedding_model
            }
        )

        try:
            # ============================================================
            # OpenAI Embeddings API 호출 (배치)
            # ============================================================
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=texts  # 여러 텍스트를 한 번에 전달
            )

            # ============================================================
            # 응답에서 임베딩 추출
            # ============================================================
            # response.data는 EmbeddingObject 리스트
            # 각 객체의 .embedding 속성이 벡터 (List[float])
            embeddings = [item.embedding for item in response.data]

            # ============================================================
            # 로그: 임베딩 생성 완료
            # ============================================================
            self.logger.info(
                "Embeddings generated successfully",
                extra={
                    "text_count": len(texts),
                    "total_tokens": response.usage.total_tokens,
                    "embedding_dimension": len(embeddings[0]) if embeddings else 0
                }
            )

            return embeddings

        except openai.AuthenticationError as e:
            self.logger.error(
                "OpenAI authentication failed",
                extra={"error": str(e)}
            )
            raise

        except openai.BadRequestError as e:
            self.logger.error(
                "Invalid embedding request",
                extra={"error": str(e), "text_count": len(texts)}
            )
            raise

        except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError) as e:
            self.logger.warning(
                "OpenAI API error (will retry)",
                extra={"error_type": type(e).__name__, "error": str(e)}
            )
            raise  # tenacity가 재시도

        except openai.APIError as e:
            self.logger.error(
                "OpenAI API error",
                extra={"error": str(e)}
            )
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """
        단일 텍스트의 임베딩 생성

        내부적으로 generate_embeddings()를 호출하여 배치 처리 로직을 재사용합니다.

        Args:
            text (str): 임베딩을 생성할 텍스트

        Returns:
            List[float]: 1536차원 임베딩 벡터

        Raises:
            ValueError: 빈 텍스트 입력 시
            openai.APIError: OpenAI API 오류

        Example:
            >>> service = EmbeddingService()
            >>> vector = await service.generate_embedding("토마토는 빨갛다")
            >>> len(vector)
            1536
            >>> isinstance(vector[0], float)
            True
        """
        # ============================================================
        # 입력 검증
        # ============================================================
        if not text.strip():
            raise ValueError("text cannot be empty")

        # ============================================================
        # 배치 처리 메서드 호출 (1개 텍스트)
        # ============================================================
        embeddings = await self.generate_embeddings([text])

        # ============================================================
        # 첫 번째 (유일한) 임베딩 반환
        # ============================================================
        return embeddings[0]

    def get_embedding_info(self) -> dict:
        """
        임베딩 모델 정보 반환

        Returns:
            dict: 임베딩 모델 정보
        """
        return {
            "model": self.embedding_model,
            "dimension": self.embedding_dimension,
            "api_key_configured": bool(settings.openai_api_key)
        }


# ============================================================
# 테스트 코드 (python -m backend.services.embedding_service 실행 시)
# ============================================================
if __name__ == "__main__":
    """임베딩 서비스 동작 테스트"""

    import asyncio

    async def test_embedding_service():
        """임베딩 서비스 테스트"""

        print("=== Embedding Service Test ===\n")

        # ============================================================
        # 1. 서비스 생성
        # ============================================================
        service = EmbeddingService()
        print(f"✅ Service initialized")
        print(f"   Model: {service.embedding_model}")
        print(f"   Dimension: {service.embedding_dimension}\n")

        # ============================================================
        # 2. 단일 텍스트 임베딩
        # ============================================================
        print("🔄 Testing single text embedding...")

        try:
            text = "토마토는 건강에 좋은 채소입니다."
            vector = await service.generate_embedding(text)

            print(f"✅ Single embedding generated")
            print(f"   Text: {text}")
            print(f"   Vector length: {len(vector)}")
            print(f"   First 5 values: {vector[:5]}\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")
            return

        # ============================================================
        # 3. 배치 임베딩 (다중 텍스트)
        # ============================================================
        print("🔄 Testing batch embeddings...")

        try:
            texts = [
                "토마토는 빨간색이다.",
                "하늘은 파란색이다.",
                "잔디는 초록색이다."
            ]
            vectors = await service.generate_embeddings(texts)

            print(f"✅ Batch embeddings generated")
            print(f"   Text count: {len(texts)}")
            print(f"   Vectors count: {len(vectors)}")
            print(f"   Each vector length: {len(vectors[0])}\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")
            return

        # ============================================================
        # 4. 유사도 계산 (간단한 코사인 유사도)
        # ============================================================
        print("🔄 Testing similarity calculation...")

        try:
            # 두 텍스트 임베딩
            text1 = "토마토 재배 방법"
            text2 = "토마토 키우기"
            text3 = "컴퓨터 프로그래밍"

            vec1 = await service.generate_embedding(text1)
            vec2 = await service.generate_embedding(text2)
            vec3 = await service.generate_embedding(text3)

            # 코사인 유사도 계산 (간단한 내적)
            import numpy as np

            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            vec3_np = np.array(vec3)

            # 정규화 (L2 norm)
            vec1_np = vec1_np / np.linalg.norm(vec1_np)
            vec2_np = vec2_np / np.linalg.norm(vec2_np)
            vec3_np = vec3_np / np.linalg.norm(vec3_np)

            sim_1_2 = np.dot(vec1_np, vec2_np)
            sim_1_3 = np.dot(vec1_np, vec3_np)

            print(f"✅ Similarity calculated")
            print(f"   '{text1}' ↔ '{text2}': {sim_1_2:.3f}")
            print(f"   '{text1}' ↔ '{text3}': {sim_1_3:.3f}")
            print(f"   (유사한 주제일수록 1에 가까움)\n")

        except ImportError:
            print("ℹ️  numpy not installed, skipping similarity test\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")

        # ============================================================
        # 5. 모델 정보 확인
        # ============================================================
        info = service.get_embedding_info()
        print(f"📊 Embedding Info: {info}")

    # ============================================================
    # asyncio 이벤트 루프 실행
    # ============================================================
    asyncio.run(test_embedding_service())
