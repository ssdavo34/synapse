"""
OCR 서비스 (PDF 텍스트 추출)
============================

목적:
    - PDF 파일에서 텍스트 추출
    - PyMuPDF (fitz) 라이브러리 사용
    - 메타데이터 추출 (페이지 수, 작성자, 생성일 등)

특징:
    - 빠르고 정확한 텍스트 추출
    - 페이지별 텍스트 추출 후 통합
    - 암호화/손상된 PDF 에러 처리
    - 텍스트 정제 (공백, 특수문자)

사용법:
    from services.ocr_service import OCRService

    service = OCRService()
    result = service.extract_text("data/uploads/document.pdf")
    print(result["text"])
    print(result["num_pages"])
"""

import fitz  # PyMuPDF
import os
from typing import Dict, Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger


class OCRService:
    """
    PDF 텍스트 추출 서비스

    PyMuPDF (fitz)를 사용하여 PDF 파일에서 텍스트를 추출합니다.
    DocumentAgent가 PDF 문서 처리 시 사용합니다.

    Attributes:
        logger (logging.Logger): JSON 로거
    """

    def __init__(self):
        """
        OCR 서비스 초기화

        PyMuPDF는 별도 초기화가 필요 없습니다.
        """
        # ============================================================
        # 로거 설정
        # ============================================================
        self.logger = setup_logger("OCRService")
        self.logger.info("OCR service initialized (PyMuPDF)")

    def extract_text(self, pdf_path: str) -> Dict[str, Any]:
        """
        PDF 파일에서 텍스트 추출

        Args:
            pdf_path (str): PDF 파일 경로

        Returns:
            Dict[str, Any]: 추출 결과
                {
                    "text": str,           # 전체 텍스트
                    "num_pages": int,      # 페이지 수
                    "metadata": dict,      # 메타데이터
                    "file_size": int       # 파일 크기 (bytes)
                }

        Raises:
            FileNotFoundError: 파일이 없을 때
            PermissionError: 읽기 권한 없을 때
            ValueError: 암호화된 PDF 또는 손상된 파일
            Exception: 기타 PDF 처리 오류

        Example:
            >>> service = OCRService()
            >>> result = service.extract_text("document.pdf")
            >>> print(f"Pages: {result['num_pages']}")
            >>> print(f"Text length: {len(result['text'])}")
        """
        # ============================================================
        # 파일 존재 확인
        # ============================================================
        if not os.path.exists(pdf_path):
            self.logger.error(
                "PDF file not found",
                extra={"path": pdf_path}
            )
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # ============================================================
        # 파일 크기 확인
        # ============================================================
        file_size = os.path.getsize(pdf_path)

        # ============================================================
        # 로그: 텍스트 추출 시작
        # ============================================================
        self.logger.info(
            "Starting PDF text extraction",
            extra={
                "path": pdf_path,
                "file_size_bytes": file_size
            }
        )

        try:
            # ============================================================
            # PDF 열기
            # ============================================================
            doc = fitz.open(pdf_path)

            # ============================================================
            # 암호화 확인
            # ============================================================
            if doc.is_encrypted:
                doc.close()
                self.logger.error("PDF is encrypted", extra={"path": pdf_path})
                raise ValueError(f"PDF is encrypted and cannot be read: {pdf_path}")

            # ============================================================
            # 페이지 수 확인
            # ============================================================
            num_pages = len(doc)

            if num_pages == 0:
                doc.close()
                self.logger.error("PDF has no pages", extra={"path": pdf_path})
                raise ValueError(f"PDF has no pages: {pdf_path}")

            # ============================================================
            # 메타데이터 추출
            # ============================================================
            metadata = self._extract_metadata(doc)

            # ============================================================
            # 페이지별 텍스트 추출
            # ============================================================
            all_text = []

            for page_num in range(num_pages):
                # 페이지 가져오기
                page = doc[page_num]

                # 텍스트 추출
                page_text = page.get_text()

                # 텍스트 정제
                cleaned_text = self.clean_text(page_text)

                if cleaned_text.strip():
                    all_text.append(cleaned_text)

                # 진행 로그 (10페이지마다)
                if (page_num + 1) % 10 == 0:
                    self.logger.info(
                        f"Processed {page_num + 1}/{num_pages} pages",
                        extra={"page_num": page_num + 1, "total_pages": num_pages}
                    )

            # ============================================================
            # PDF 닫기
            # ============================================================
            doc.close()

            # ============================================================
            # 전체 텍스트 통합
            # ============================================================
            full_text = "\n\n".join(all_text)

            # ============================================================
            # 빈 텍스트 확인
            # ============================================================
            if not full_text.strip():
                self.logger.warning(
                    "No text extracted from PDF",
                    extra={"path": pdf_path, "num_pages": num_pages}
                )
                raise ValueError(f"No text could be extracted from PDF: {pdf_path}")

            # ============================================================
            # 로그: 텍스트 추출 완료
            # ============================================================
            self.logger.info(
                "PDF text extraction completed",
                extra={
                    "path": pdf_path,
                    "num_pages": num_pages,
                    "text_length": len(full_text),
                    "file_size_bytes": file_size
                }
            )

            # ============================================================
            # 결과 반환
            # ============================================================
            return {
                "text": full_text,
                "num_pages": num_pages,
                "metadata": metadata,
                "file_size": file_size
            }

        except PermissionError as e:
            # ============================================================
            # 읽기 권한 오류
            # ============================================================
            self.logger.error(
                "Permission denied reading PDF",
                extra={"path": pdf_path, "error": str(e)}
            )
            raise PermissionError(f"Permission denied: {pdf_path}")

        except fitz.FileDataError as e:
            # ============================================================
            # 손상된 PDF 파일
            # ============================================================
            self.logger.error(
                "Corrupted PDF file",
                extra={"path": pdf_path, "error": str(e)}
            )
            raise ValueError(f"Corrupted PDF file: {pdf_path}")

        except Exception as e:
            # ============================================================
            # 기타 오류
            # ============================================================
            self.logger.error(
                "PDF processing error",
                extra={"path": pdf_path, "error": str(e)},
                exc_info=True
            )
            raise Exception(f"Failed to process PDF: {str(e)}")

    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """
        PDF 메타데이터 추출

        Args:
            doc (fitz.Document): PyMuPDF 문서 객체

        Returns:
            Dict[str, Any]: 메타데이터 딕셔너리
        """
        # ============================================================
        # PyMuPDF metadata 딕셔너리
        # ============================================================
        metadata = doc.metadata or {}

        # ============================================================
        # 주요 메타데이터 추출
        # ============================================================
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "format": metadata.get("format", "PDF")
        }

    def clean_text(self, text: str) -> str:
        """
        텍스트 정제

        PDF에서 추출한 텍스트의 불필요한 문자를 제거합니다.

        Args:
            text (str): 원본 텍스트

        Returns:
            str: 정제된 텍스트

        처리 내용:
            - NULL 문자 제거
            - 연속된 공백 정리
            - 연속된 개행 정리 (3개 이상 → 2개)
        """
        import re

        # ============================================================
        # NULL 문자 제거
        # ============================================================
        text = text.replace('\x00', '')

        # ============================================================
        # 연속된 공백을 하나로
        # ============================================================
        text = re.sub(r' +', ' ', text)

        # ============================================================
        # 연속된 개행(3개 이상)을 2개로
        # ============================================================
        text = re.sub(r'\n{3,}', '\n\n', text)

        # ============================================================
        # 앞뒤 공백 제거
        # ============================================================
        text = text.strip()

        return text

    def get_page_count(self, pdf_path: str) -> int:
        """
        PDF 페이지 수만 빠르게 가져오기

        텍스트 추출 없이 페이지 수만 확인할 때 사용합니다.

        Args:
            pdf_path (str): PDF 파일 경로

        Returns:
            int: 페이지 수

        Raises:
            FileNotFoundError: 파일이 없을 때
            Exception: PDF 처리 오류
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception as e:
            self.logger.error(
                "Failed to get page count",
                extra={"path": pdf_path, "error": str(e)}
            )
            raise


# ============================================================
# 테스트 코드 (python -m backend.services.ocr_service 실행 시)
# ============================================================
if __name__ == "__main__":
    """OCR 서비스 동작 테스트"""

    print("=== OCR Service Test ===\n")

    # ============================================================
    # 1. 서비스 생성
    # ============================================================
    service = OCRService()
    print("✅ OCR service initialized\n")

    # ============================================================
    # 2. 테스트 PDF 생성 (샘플)
    # ============================================================
    print("🔄 Creating test PDF...")

    # 간단한 테스트 PDF 생성
    test_pdf_path = "data/uploads/test_ocr.pdf"

    # 디렉토리 확인
    os.makedirs(os.path.dirname(test_pdf_path), exist_ok=True)

    # PyMuPDF로 간단한 PDF 생성
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "이것은 테스트 PDF입니다.")
    page.insert_text((50, 130), "OCR Service 테스트를 위한 샘플 텍스트입니다.")
    page.insert_text((50, 160), "PyMuPDF를 사용하여 텍스트를 추출합니다.")

    # 두 번째 페이지 추가
    page2 = doc.new_page()
    page2.insert_text((50, 100), "두 번째 페이지입니다.")
    page2.insert_text((50, 130), "여러 페이지에서 텍스트를 추출할 수 있습니다.")

    doc.save(test_pdf_path)
    doc.close()

    print(f"✅ Test PDF created: {test_pdf_path}\n")

    # ============================================================
    # 3. 텍스트 추출 테스트
    # ============================================================
    print("🔄 Testing text extraction...")

    try:
        result = service.extract_text(test_pdf_path)

        print(f"✅ Text extraction successful")
        print(f"   Pages: {result['num_pages']}")
        print(f"   Text length: {len(result['text'])} characters")
        print(f"   File size: {result['file_size']} bytes")
        print(f"\n   Extracted text preview:")
        print(f"   {result['text'][:200]}...")
        print(f"\n   Metadata:")
        for key, value in result['metadata'].items():
            if value:
                print(f"     {key}: {value}")
        print()

    except Exception as e:
        print(f"❌ Error: {e}\n")

    # ============================================================
    # 4. 페이지 수 확인 테스트
    # ============================================================
    print("🔄 Testing page count...")

    try:
        page_count = service.get_page_count(test_pdf_path)
        print(f"✅ Page count: {page_count}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

    # ============================================================
    # 5. 에러 케이스 테스트
    # ============================================================
    print("🔄 Testing error cases...")

    # 존재하지 않는 파일
    try:
        service.extract_text("nonexistent.pdf")
        print("❌ Should have raised FileNotFoundError")
    except FileNotFoundError:
        print("✅ FileNotFoundError correctly raised")

    print("\n=== Test completed ===")
