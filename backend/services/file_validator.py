"""
File Validator Module

파일 업로드 보안 검증을 담당하는 모듈입니다.
파일 크기, MIME 타입, 확장자, 악성 코드 패턴을 검증합니다.

Features:
    - 파일 크기 검증 (최대 50MB)
    - MIME 타입 검증 (PDF, TXT, MD만 허용)
    - 파일 확장자 검증
    - 악성 코드 시그니처 체크

Examples:
    >>> validator = FileValidator()
    >>> result = validator.validate_file("document.pdf")
    >>> if result["is_valid"]:
    ...     print("파일 검증 통과")
    >>> else:
    ...     print(f"검증 실패: {result['error']}")
"""

import os
import mimetypes
from typing import Dict, List, Optional, Any
from pathlib import Path

from backend.utils.logger import setup_logger

# Logger 설정
logger = setup_logger("FileValidator")


class FileValidator:
    """
    파일 보안 검증 클래스

    업로드된 파일의 보안성을 검증합니다:
    1. 파일 크기 제한 확인
    2. MIME 타입 화이트리스트 확인
    3. 확장자 검증
    4. 악성 코드 패턴 스캔

    Attributes:
        max_file_size (int): 최대 파일 크기 (바이트), 기본값 50MB
        allowed_extensions (set): 허용된 파일 확장자 집합
        allowed_mime_types (set): 허용된 MIME 타입 집합
        malicious_patterns (list): 악성 코드 시그니처 패턴 리스트

    Examples:
        >>> validator = FileValidator(max_file_size=10 * 1024 * 1024)  # 10MB
        >>> result = validator.validate_file("upload.pdf")
        >>> print(result)
        {'is_valid': True, 'file_path': 'upload.pdf', 'size': 2048,
         'mime_type': 'application/pdf', 'extension': '.pdf'}
    """

    # 최대 파일 크기: 50MB (바이트 단위)
    DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024

    # 허용된 파일 확장자 (소문자)
    ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md'}

    # 허용된 MIME 타입
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'text/plain',
        'text/markdown',
        'text/x-markdown',
    }

    # 악성 코드 시그니처 패턴 (간단한 바이너리 시그니처)
    # 실제 프로덕션에서는 더 정교한 AV 엔진 사용 권장
    MALICIOUS_PATTERNS = [
        # PE 실행 파일 헤더
        b'MZ\x90\x00',  # DOS MZ 헤더
        # 스크립트 악성 패턴
        b'<script',  # HTML 스크립트 태그
        b'javascript:',  # JavaScript URI 스키마
        b'eval(',  # JavaScript eval 함수
        # Shell 명령 패턴
        b'<?php',  # PHP 태그
        b'exec(',  # 명령 실행 함수
        b'system(',  # 시스템 명령 실행
        b'passthru(',  # 명령 실행 함수
        # SQL Injection 패턴
        b'DROP TABLE',
        b'DELETE FROM',
        b'INSERT INTO',
        # 매크로 패턴
        b'AutoOpen',  # Word 자동 실행 매크로
        b'AutoExec',  # Excel 자동 실행 매크로
    ]

    def __init__(
        self,
        max_file_size: Optional[int] = None,
        allowed_extensions: Optional[set] = None,
        allowed_mime_types: Optional[set] = None
    ):
        """
        FileValidator 초기화

        Args:
            max_file_size: 최대 파일 크기 (바이트). None이면 기본값 50MB 사용
            allowed_extensions: 허용된 확장자 집합. None이면 기본값 사용
            allowed_mime_types: 허용된 MIME 타입 집합. None이면 기본값 사용

        Examples:
            >>> # 기본 설정 사용
            >>> validator = FileValidator()
            >>>
            >>> # 커스텀 설정
            >>> validator = FileValidator(
            ...     max_file_size=10 * 1024 * 1024,  # 10MB
            ...     allowed_extensions={'.pdf', '.docx'}
            ... )
        """
        self.max_file_size = max_file_size or self.DEFAULT_MAX_FILE_SIZE
        self.allowed_extensions = allowed_extensions or self.ALLOWED_EXTENSIONS
        self.allowed_mime_types = allowed_mime_types or self.ALLOWED_MIME_TYPES
        self.malicious_patterns = self.MALICIOUS_PATTERNS

        logger.info(
            "FileValidator initialized",
            extra={
                "max_size_mb": self.max_file_size / (1024 * 1024),
                "allowed_extensions": list(self.allowed_extensions),
                "allowed_mime_types": list(self.allowed_mime_types)
            }
        )

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        파일 종합 검증

        파일이 모든 보안 검증을 통과하는지 확인합니다:
        1. 파일 존재 확인
        2. 파일 크기 검증
        3. 확장자 검증
        4. MIME 타입 검증
        5. 악성 코드 패턴 스캔

        Args:
            file_path: 검증할 파일의 경로

        Returns:
            검증 결과 딕셔너리:
            {
                'is_valid': bool,  # 전체 검증 통과 여부
                'file_path': str,  # 파일 경로
                'size': int,  # 파일 크기 (바이트)
                'mime_type': str,  # 탐지된 MIME 타입
                'extension': str,  # 파일 확장자
                'checks': {  # 개별 검증 항목 결과
                    'exists': bool,
                    'size': bool,
                    'extension': bool,
                    'mime_type': bool,
                    'malicious': bool
                },
                'error': str  # 검증 실패 시 에러 메시지 (선택적)
            }

        Examples:
            >>> validator = FileValidator()
            >>> result = validator.validate_file("safe_document.pdf")
            >>> if result['is_valid']:
            ...     print(f"파일 안전: {result['size']} bytes")
            >>> else:
            ...     print(f"검증 실패: {result['error']}")
        """
        logger.info("Starting file validation", extra={"file_path": file_path})

        # 결과 딕셔너리 초기화
        result = {
            'is_valid': False,
            'file_path': file_path,
            'size': 0,
            'mime_type': '',
            'extension': '',
            'checks': {
                'exists': False,
                'size': False,
                'extension': False,
                'mime_type': False,
                'malicious': False
            }
        }

        # 1. 파일 존재 확인
        if not os.path.exists(file_path):
            result['error'] = f"File not found: {file_path}"
            logger.error("File validation failed", extra={"error": result['error']})
            return result

        if not os.path.isfile(file_path):
            result['error'] = f"Path is not a file: {file_path}"
            logger.error("File validation failed", extra={"error": result['error']})
            return result

        result['checks']['exists'] = True

        # 2. 파일 크기 검증
        try:
            size_valid = self.check_file_size(file_path)
            file_size = os.path.getsize(file_path)
            result['size'] = file_size
            result['checks']['size'] = size_valid

            if not size_valid:
                result['error'] = (
                    f"File size {file_size} bytes exceeds maximum "
                    f"{self.max_file_size} bytes ({self.max_file_size / (1024*1024):.1f}MB)"
                )
                logger.error("File size validation failed", extra=result)
                return result
        except Exception as e:
            result['error'] = f"Error checking file size: {str(e)}"
            logger.error("File size check error", extra={"error": str(e)})
            return result

        # 3. 확장자 검증
        extension = Path(file_path).suffix.lower()
        result['extension'] = extension

        if extension not in self.allowed_extensions:
            result['error'] = (
                f"Extension '{extension}' not allowed. "
                f"Allowed: {', '.join(self.allowed_extensions)}"
            )
            logger.error("File extension validation failed", extra=result)
            return result

        result['checks']['extension'] = True

        # 4. MIME 타입 검증
        try:
            mime_valid, mime_type = self.check_mime_type(file_path)
            result['mime_type'] = mime_type
            result['checks']['mime_type'] = mime_valid

            if not mime_valid:
                result['error'] = (
                    f"MIME type '{mime_type}' not allowed. "
                    f"Allowed: {', '.join(self.allowed_mime_types)}"
                )
                logger.error("MIME type validation failed", extra=result)
                return result
        except Exception as e:
            result['error'] = f"Error checking MIME type: {str(e)}"
            logger.error("MIME type check error", extra={"error": str(e)})
            return result

        # 5. 악성 코드 패턴 스캔
        try:
            is_clean = self.scan_malicious_patterns(file_path)
            result['checks']['malicious'] = is_clean

            if not is_clean:
                result['error'] = "Malicious pattern detected in file"
                logger.warning("Malicious pattern detected", extra={"file_path": file_path})
                return result
        except Exception as e:
            result['error'] = f"Error scanning for malicious patterns: {str(e)}"
            logger.error("Malicious pattern scan error", extra={"error": str(e)})
            return result

        # 모든 검증 통과
        result['is_valid'] = True
        logger.info(
            "File validation passed",
            extra={
                "file_path": file_path,
                "size": result['size'],
                "mime_type": result['mime_type'],
                "extension": result['extension']
            }
        )

        return result

    def check_file_size(self, file_path: str) -> bool:
        """
        파일 크기 검증

        파일 크기가 최대 허용 크기 이하인지 확인합니다.

        Args:
            file_path: 검증할 파일의 경로

        Returns:
            파일 크기가 허용 범위 내이면 True, 아니면 False

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            OSError: 파일 크기를 읽을 수 없을 때

        Examples:
            >>> validator = FileValidator(max_file_size=1024*1024)  # 1MB
            >>> validator.check_file_size("small.txt")  # 500KB 파일
            True
            >>> validator.check_file_size("large.pdf")  # 2MB 파일
            False
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        is_valid = file_size <= self.max_file_size

        logger.debug(
            "File size check",
            extra={
                "file_path": file_path,
                "size_bytes": file_size,
                "size_mb": file_size / (1024 * 1024),
                "max_mb": self.max_file_size / (1024 * 1024),
                "is_valid": is_valid
            }
        )

        return is_valid

    def check_mime_type(self, file_path: str) -> tuple[bool, str]:
        """
        MIME 타입 검증

        파일의 MIME 타입을 탐지하고 허용된 타입인지 확인합니다.
        파일 확장자와 내용을 기반으로 MIME 타입을 추정합니다.

        Args:
            file_path: 검증할 파일의 경로

        Returns:
            (is_valid, mime_type) 튜플:
                - is_valid: MIME 타입이 허용 목록에 있으면 True
                - mime_type: 탐지된 MIME 타입 문자열

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때

        Examples:
            >>> validator = FileValidator()
            >>> is_valid, mime_type = validator.check_mime_type("doc.pdf")
            >>> print(f"Valid: {is_valid}, Type: {mime_type}")
            Valid: True, Type: application/pdf
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # mimetypes 모듈을 사용한 MIME 타입 추정
        mime_type, _ = mimetypes.guess_type(file_path)

        # MIME 타입을 추정할 수 없는 경우
        if mime_type is None:
            # 파일 내용의 첫 바이트를 읽어 PDF 시그니처 확인
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(5)
                    if header.startswith(b'%PDF-'):
                        mime_type = 'application/pdf'
                    else:
                        # 텍스트 파일로 간주
                        mime_type = 'text/plain'
            except Exception as e:
                logger.warning(
                    "Failed to read file header for MIME detection",
                    extra={
                        "file_path": file_path,
                        "error": str(e)
                    }
                )
                mime_type = 'application/octet-stream'

        is_valid = mime_type in self.allowed_mime_types

        logger.debug(
            "MIME type check",
            extra={
                "file_path": file_path,
                "mime_type": mime_type,
                "is_valid": is_valid
            }
        )

        return is_valid, mime_type

    def scan_malicious_patterns(self, file_path: str) -> bool:
        """
        악성 코드 패턴 스캔

        파일 내용에서 알려진 악성 코드 시그니처를 검색합니다.
        간단한 바이너리 패턴 매칭을 사용하여 기본적인 보안 검증을 수행합니다.

        주의: 이 메서드는 기본적인 검증만 제공합니다.
        프로덕션 환경에서는 ClamAV 같은 전문 안티바이러스 엔진 사용을 권장합니다.

        Args:
            file_path: 스캔할 파일의 경로

        Returns:
            악성 패턴이 발견되지 않으면 True (안전),
            악성 패턴이 발견되면 False (위험)

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            PermissionError: 파일을 읽을 권한이 없을 때

        Examples:
            >>> validator = FileValidator()
            >>> is_safe = validator.scan_malicious_patterns("document.pdf")
            >>> if is_safe:
            ...     print("파일에서 악성 패턴이 발견되지 않았습니다")
            >>> else:
            ...     print("경고: 악성 패턴이 탐지되었습니다!")
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # 파일을 바이너리 모드로 읽기
            with open(file_path, 'rb') as f:
                content = f.read()

            # 각 악성 패턴에 대해 검사
            for pattern in self.malicious_patterns:
                if pattern in content:
                    logger.warning(
                        "Malicious pattern detected",
                        extra={
                            "file_path": file_path,
                            "pattern": pattern.decode('utf-8', errors='replace')[:50]
                        }
                    )
                    return False

            # 추가 검증: 소문자로 변환하여 대소문자 무시 패턴 체크
            content_lower = content.lower()

            # 대소문자 무시 패턴
            case_insensitive_patterns = [
                b'autoopen',
                b'autoexec',
                b'drop table',
                b'delete from',
            ]

            for pattern in case_insensitive_patterns:
                if pattern in content_lower:
                    logger.warning(
                        "Malicious pattern detected (case-insensitive)",
                        extra={
                            "file_path": file_path,
                            "pattern": pattern.decode('utf-8', errors='replace')
                        }
                    )
                    return False

            logger.debug(
                "Malicious pattern scan completed - no threats found",
                extra={
                    "file_path": file_path,
                    "file_size": len(content)
                }
            )

            return True

        except PermissionError as e:
            logger.error("Permission denied reading file", extra={"file_path": file_path})
            raise
        except Exception as e:
            logger.error(
                "Error during malicious pattern scan",
                extra={
                    "file_path": file_path,
                    "error": str(e)
                }
            )
            raise


# 테스트 코드
if __name__ == "__main__":
    import tempfile

    print("=== File Validator Test ===\n")

    # FileValidator 인스턴스 생성
    validator = FileValidator()
    print("✅ FileValidator initialized\n")

    # 테스트용 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. 안전한 PDF 파일 테스트
        print("🔄 Test 1: Valid PDF file")
        safe_pdf_path = os.path.join(temp_dir, "safe.pdf")
        with open(safe_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n')
            f.write(b'This is a safe PDF content.\n')
            f.write(b'No malicious patterns here.\n')

        result = validator.validate_file(safe_pdf_path)
        if result['is_valid']:
            print(f"✅ Safe PDF validation passed")
            print(f"   Size: {result['size']} bytes")
            print(f"   MIME: {result['mime_type']}\n")
        else:
            print(f"❌ Validation failed: {result.get('error')}\n")

        # 2. 안전한 텍스트 파일 테스트
        print("🔄 Test 2: Valid text file")
        safe_txt_path = os.path.join(temp_dir, "safe.txt")
        with open(safe_txt_path, 'w', encoding='utf-8') as f:
            f.write("This is a safe text file.\n")
            f.write("안전한 텍스트 파일입니다.\n")

        result = validator.validate_file(safe_txt_path)
        if result['is_valid']:
            print(f"✅ Safe text file validation passed")
            print(f"   Size: {result['size']} bytes")
            print(f"   MIME: {result['mime_type']}\n")
        else:
            print(f"❌ Validation failed: {result.get('error')}\n")

        # 3. 악성 패턴 포함 파일 테스트
        print("🔄 Test 3: File with malicious pattern")
        malicious_path = os.path.join(temp_dir, "malicious.txt")
        with open(malicious_path, 'wb') as f:
            f.write(b'Normal content\n')
            f.write(b'<script>alert("xss")</script>\n')  # 악성 패턴

        result = validator.validate_file(malicious_path)
        if not result['is_valid']:
            print(f"✅ Malicious pattern correctly detected")
            print(f"   Error: {result.get('error')}\n")
        else:
            print(f"❌ Failed to detect malicious pattern\n")

        # 4. 파일 크기 초과 테스트
        print("🔄 Test 4: File size limit")
        small_validator = FileValidator(max_file_size=100)  # 100 bytes만 허용
        large_file_path = os.path.join(temp_dir, "large.txt")
        with open(large_file_path, 'w') as f:
            f.write("X" * 200)  # 200 bytes

        result = small_validator.validate_file(large_file_path)
        if not result['is_valid'] and 'size' in result.get('error', ''):
            print(f"✅ File size limit correctly enforced")
            print(f"   Error: {result.get('error')}\n")
        else:
            print(f"❌ Failed to enforce size limit\n")

        # 5. 허용되지 않은 확장자 테스트
        print("🔄 Test 5: Invalid extension")
        invalid_ext_path = os.path.join(temp_dir, "file.exe")
        with open(invalid_ext_path, 'w') as f:
            f.write("test content")

        result = validator.validate_file(invalid_ext_path)
        if not result['is_valid'] and 'extension' in result.get('error', '').lower():
            print(f"✅ Invalid extension correctly rejected")
            print(f"   Error: {result.get('error')}\n")
        else:
            print(f"❌ Failed to reject invalid extension\n")

        # 6. 존재하지 않는 파일 테스트
        print("🔄 Test 6: Non-existent file")
        result = validator.validate_file("nonexistent_file.pdf")
        if not result['is_valid'] and 'not found' in result.get('error', '').lower():
            print(f"✅ Non-existent file correctly handled")
            print(f"   Error: {result.get('error')}\n")
        else:
            print(f"❌ Failed to handle non-existent file\n")

        # 7. Markdown 파일 테스트
        print("🔄 Test 7: Valid markdown file")
        md_path = os.path.join(temp_dir, "document.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Markdown Document\n")
            f.write("This is **safe** markdown content.\n")

        result = validator.validate_file(md_path)
        if result['is_valid']:
            print(f"✅ Markdown file validation passed")
            print(f"   Size: {result['size']} bytes")
            print(f"   MIME: {result['mime_type']}\n")
        else:
            print(f"❌ Validation failed: {result.get('error')}\n")

    print("=== All tests completed ===")
