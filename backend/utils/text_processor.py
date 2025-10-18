"""
텍스트 처리 유틸리티
===================

목적:
    - 긴 텍스트를 적절한 크기로 분할 (청킹)
    - 문장 경계를 고려한 지능형 분할
    - 오버랩으로 문맥 보존
    - 텍스트 정제 (공백, 개행 정리)

사용 사례:
    - DocumentAgent: PDF 텍스트를 500자 청크로 분할하여 임베딩 생성
    - SummaryAgent: Map-Reduce 요약 시 청크 단위 처리

특징:
    - 문장 경계 고려 (마침표, 개행, 느낌표, 물음표)
    - 청크 간 오버랩으로 문맥 손실 최소화
    - 한글 및 영어 텍스트 모두 지원

사용법:
    from utils.text_processor import TextProcessor

    processor = TextProcessor()
    chunks = processor.chunk_text(long_text, chunk_size=500, overlap=50)
"""

import re
from typing import List
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger


class TextProcessor:
    """
    텍스트 처리 및 청킹 클래스

    긴 문서를 적절한 크기의 청크로 분할하고 텍스트를 정제합니다.
    문장 경계를 고려하여 의미 단위를 유지합니다.

    Attributes:
        logger (logging.Logger): JSON 로거
        sentence_endings (List[str]): 문장 종료 기호
    """

    def __init__(self):
        """
        TextProcessor 초기화

        로거를 설정하고 문장 종료 패턴을 정의합니다.
        """
        # ============================================================
        # 로거 설정
        # ============================================================
        self.logger = setup_logger("TextProcessor")

        # ============================================================
        # 문장 종료 기호 정의
        # ============================================================
        # 한글: 마침표(.), 느낌표(!), 물음표(?)
        # 영어: 마침표(.), 느낌표(!), 물음표(?)
        # 개행(\n)도 문장 구분자로 사용
        self.sentence_endings = ['.', '!', '?', '\n']

        self.logger.info("TextProcessor initialized")

    def clean_text(self, text: str) -> str:
        """
        텍스트 정제

        불필요한 공백과 개행을 정리합니다.

        Args:
            text (str): 정제할 텍스트

        Returns:
            str: 정제된 텍스트

        처리 내용:
            - 연속된 공백을 하나로 통합
            - 연속된 개행(3개 이상)을 2개로 통합
            - 앞뒤 공백 제거

        Example:
            >>> processor = TextProcessor()
            >>> text = "안녕하세요.    여러 공백이    있습니다.\\n\\n\\n\\n많은 개행"
            >>> clean = processor.clean_text(text)
            >>> print(clean)
            "안녕하세요. 여러 공백이 있습니다.\\n\\n많은 개행"
        """
        # ============================================================
        # 1. 연속된 공백을 하나로
        # ============================================================
        # "안녕   하세요" → "안녕 하세요"
        text = re.sub(r' +', ' ', text)

        # ============================================================
        # 2. 연속된 개행(3개 이상)을 2개로
        # ============================================================
        # "단락1\n\n\n\n단락2" → "단락1\n\n단락2"
        # 단락 구분은 유지하되, 과도한 개행 제거
        text = re.sub(r'\n{3,}', '\n\n', text)

        # ============================================================
        # 3. 앞뒤 공백 제거
        # ============================================================
        text = text.strip()

        return text

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """
        텍스트를 청크로 분할

        문장 경계를 고려하여 지능적으로 분할합니다.
        청크 간 오버랩으로 문맥을 보존합니다.

        Args:
            text (str): 분할할 텍스트
            chunk_size (int): 청크 크기 (문자 수 기준)
                기본값: 500자
            overlap (int): 청크 간 오버랩 크기 (문자 수)
                기본값: 50자

        Returns:
            List[str]: 청크 리스트

        동작 방식:
            1. 텍스트를 chunk_size 단위로 분할
            2. 분할 지점 근처에서 문장 경계 찾기
            3. 문장 경계가 있으면 그곳에서 분할
            4. 다음 청크는 overlap만큼 이전 청크와 겹침

        Example:
            >>> processor = TextProcessor()
            >>> text = "문장1입니다. 문장2입니다. 문장3입니다. " * 50
            >>> chunks = processor.chunk_text(text, chunk_size=500, overlap=50)
            >>> len(chunks)
            3
            >>> len(chunks[0])
            ~500
        """
        # ============================================================
        # 입력 검증
        # ============================================================
        if not text or not text.strip():
            self.logger.warning("Empty text provided for chunking")
            return []

        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        # ============================================================
        # 텍스트 정제
        # ============================================================
        text = self.clean_text(text)

        # ============================================================
        # 텍스트가 chunk_size보다 작으면 그대로 반환
        # ============================================================
        if len(text) <= chunk_size:
            self.logger.info(
                f"Text shorter than chunk_size, returning as single chunk",
                extra={"text_length": len(text), "chunk_size": chunk_size}
            )
            return [text]

        # ============================================================
        # 청킹 로직
        # ============================================================
        chunks = []
        start = 0

        while start < len(text):
            # ============================================================
            # 청크 끝 위치 계산
            # ============================================================
            end = start + chunk_size

            # ============================================================
            # 마지막 청크인 경우
            # ============================================================
            if end >= len(text):
                chunks.append(text[start:])
                break

            # ============================================================
            # 문장 경계 찾기 (end 근처 ±50자 범위)
            # ============================================================
            # 이상적인 분할 지점: end 위치
            # 검색 범위: [end-50, end+50]
            search_start = max(end - 50, start)
            search_end = min(end + 50, len(text))

            boundary_pos = self._find_sentence_boundary(
                text,
                search_start,
                search_end,
                preferred_pos=end
            )

            # ============================================================
            # 문장 경계를 찾았으면 그곳에서 분할
            # ============================================================
            if boundary_pos:
                actual_end = boundary_pos
            else:
                # 문장 경계를 못 찾으면 chunk_size 그대로 사용
                actual_end = end

            # ============================================================
            # 청크 추가
            # ============================================================
            chunk = text[start:actual_end].strip()
            if chunk:  # 빈 청크는 제외
                chunks.append(chunk)

            # ============================================================
            # 다음 청크 시작 위치 (오버랩 적용)
            # ============================================================
            # 이전 청크의 끝 부분과 오버랩
            next_start = actual_end - overlap

            # 무한 루프 방지: start가 진전되지 않으면 강제 이동
            if next_start <= start:
                next_start = actual_end

            start = next_start

        # ============================================================
        # 로그: 청킹 완료
        # ============================================================
        self.logger.info(
            "Text chunking completed",
            extra={
                "original_length": len(text),
                "chunk_count": len(chunks),
                "avg_chunk_size": sum(len(c) for c in chunks) // len(chunks) if chunks else 0
            }
        )

        return chunks

    def _find_sentence_boundary(
        self,
        text: str,
        start: int,
        end: int,
        preferred_pos: int
    ) -> int:
        """
        텍스트 내에서 문장 경계 찾기

        Args:
            text (str): 전체 텍스트
            start (int): 검색 시작 위치
            end (int): 검색 종료 위치
            preferred_pos (int): 선호하는 분할 위치

        Returns:
            int: 문장 경계 위치 (찾지 못하면 0)

        동작:
            - [start, end] 범위에서 문장 종료 기호 검색
            - 여러 개 있으면 preferred_pos에 가장 가까운 것 선택
        """
        # ============================================================
        # 검색 범위 내에서 문장 종료 기호 찾기
        # ============================================================
        boundaries = []

        for i in range(start, end):
            if i < len(text) and text[i] in self.sentence_endings:
                # 문장 종료 기호 다음 위치를 경계로 설정
                boundaries.append(i + 1)

        # ============================================================
        # 문장 경계가 없으면 0 반환
        # ============================================================
        if not boundaries:
            return 0

        # ============================================================
        # preferred_pos에 가장 가까운 경계 선택
        # ============================================================
        closest_boundary = min(
            boundaries,
            key=lambda pos: abs(pos - preferred_pos)
        )

        return closest_boundary

    def get_text_stats(self, text: str) -> dict:
        """
        텍스트 통계 정보 반환

        Args:
            text (str): 분석할 텍스트

        Returns:
            dict: 텍스트 통계
        """
        return {
            "length": len(text),
            "lines": text.count('\n') + 1,
            "words": len(text.split()),
            "sentences": sum(text.count(ending) for ending in self.sentence_endings)
        }


# ============================================================
# 테스트 코드 (python -m backend.utils.text_processor 실행 시)
# ============================================================
if __name__ == "__main__":
    """텍스트 프로세서 동작 테스트"""

    print("=== TextProcessor Test ===\n")

    # ============================================================
    # 1. 프로세서 생성
    # ============================================================
    processor = TextProcessor()
    print("✅ TextProcessor initialized\n")

    # ============================================================
    # 2. 텍스트 정제 테스트
    # ============================================================
    print("🔄 Testing text cleaning...")

    dirty_text = "안녕하세요.    여러   공백이    있습니다.\n\n\n\n\n많은 개행이 있습니다."
    clean = processor.clean_text(dirty_text)

    print(f"Original: {repr(dirty_text)}")
    print(f"Cleaned:  {repr(clean)}")
    print()

    # ============================================================
    # 3. 청킹 테스트 - 짧은 텍스트
    # ============================================================
    print("🔄 Testing chunking (short text)...")

    short_text = "이것은 짧은 텍스트입니다."
    chunks = processor.chunk_text(short_text, chunk_size=500)

    print(f"Text length: {len(short_text)}")
    print(f"Chunks: {len(chunks)}")
    print(f"Chunk: {chunks[0]}\n")

    # ============================================================
    # 4. 청킹 테스트 - 긴 텍스트
    # ============================================================
    print("🔄 Testing chunking (long text)...")

    long_text = "문장입니다. " * 100  # ~1400자
    chunks = processor.chunk_text(long_text, chunk_size=500, overlap=50)

    print(f"Original length: {len(long_text)}")
    print(f"Chunk count: {len(chunks)}")
    print(f"First chunk length: {len(chunks[0])}")
    print(f"Last chunk length: {len(chunks[-1])}")

    # 오버랩 확인
    if len(chunks) > 1:
        overlap_match = any(
            chunks[i][-30:] in chunks[i+1]
            for i in range(len(chunks)-1)
        )
        print(f"Overlap detected: {overlap_match}")
    print()

    # ============================================================
    # 5. 문장 경계 고려 테스트
    # ============================================================
    print("🔄 Testing sentence boundary detection...")

    text_with_sentences = """
    토마토는 건강에 좋은 채소입니다. 비타민C가 풍부합니다.
    토마토를 재배하려면 햇빛이 중요합니다! 물 주기도 신경써야 합니다?
    """ * 20  # 충분히 긴 텍스트

    chunks = processor.chunk_text(text_with_sentences, chunk_size=200, overlap=20)

    print(f"Text length: {len(text_with_sentences)}")
    print(f"Chunks: {len(chunks)}")
    print(f"\nFirst chunk preview:")
    print(chunks[0][:150] + "...")
    print(f"\nLast char of first chunk: {repr(chunks[0][-10:])}")
    print()

    # ============================================================
    # 6. 텍스트 통계 테스트
    # ============================================================
    print("🔄 Testing text statistics...")

    stats = processor.get_text_stats(text_with_sentences)
    print(f"Stats: {stats}")
