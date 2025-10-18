"""
통합 로깅 시스템
================

목적:
    - 전체 애플리케이션에서 일관된 로깅 포맷 제공
    - JSON 형식으로 구조화된 로그 출력 (파싱 및 분석 용이)
    - stdout으로 출력하여 Docker/Kubernetes 환경에 적합

특징:
    - JSON 포맷: 로그 분석 도구와 쉽게 통합 가능
    - 다중 레벨 지원: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - Extra 필드: 추가 컨텍스트 정보 포함 가능
    - 중복 방지: 동일 로거 재생성 시 기존 핸들러 재사용

사용법:
    from backend.utils.logger import setup_logger
    logger = setup_logger("MyClass")
    logger.info("작업 시작", extra={"user_id": 123})
"""

import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    JSON 포맷 로거 생성

    Args:
        name (str): 로거 이름 (보통 클래스명 또는 모듈명 사용)
            예: "DocumentAgent", "RAGAgent"
        level (str): 로그 레벨 (대소문자 구분 안 함)
            - "DEBUG": 디버깅 정보 (개발용)
            - "INFO": 일반 정보 (기본값)
            - "WARNING": 경고 메시지
            - "ERROR": 에러 메시지
            - "CRITICAL": 치명적 에러

    Returns:
        logging.Logger: 설정된 로거 인스턴스

    Example:
        >>> logger = setup_logger("MyAgent", level="DEBUG")
        >>> logger.info("처리 시작", extra={"items": 10})
        {"asctime": "2025-01-15 10:00:00", "name": "MyAgent",
         "levelname": "INFO", "message": "처리 시작", "items": 10}
    """

    # ============================================================
    # 로거 생성 (Python 표준 logging 사용)
    # ============================================================
    logger = logging.getLogger(name)

    # ============================================================
    # 중복 방지: 이미 핸들러가 있으면 재사용
    # ============================================================
    # 동일한 로거를 여러 번 setup_logger()로 생성해도
    # 핸들러가 중복 추가되지 않도록 방지
    if logger.handlers:
        return logger

    # ============================================================
    # 로그 레벨 설정
    # ============================================================
    # 문자열 레벨을 logging 상수로 변환 (예: "INFO" → logging.INFO)
    # 잘못된 레벨이 들어오면 기본값 INFO 사용
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # ============================================================
    # 콘솔 핸들러 생성 (stdout으로 출력)
    # ============================================================
    # stdout 사용 이유:
    # - Docker/K8s 환경에서 로그 수집이 용이
    # - 파일 로깅보다 클라우드 환경에 적합
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # ============================================================
    # JSON 포맷터 설정 (pythonjsonlogger 사용)
    # ============================================================
    # 각 로그 메시지를 JSON 객체로 변환
    # fmt: JSON에 포함될 필드 지정
    # datefmt: 시간 포맷
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # ============================================================
    # 핸들러를 로거에 추가
    # ============================================================
    logger.addHandler(console_handler)

    # ============================================================
    # 상위 로거로 전파 방지 (중복 출력 방지)
    # ============================================================
    # propagate=False로 설정하면 상위(root) 로거로 메시지가
    # 전파되지 않아 중복 출력을 방지
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    기존 로거 가져오기 (없으면 새로 생성)

    setup_logger()의 편의 래퍼 함수
    이미 생성된 로거가 있으면 재사용하고, 없으면 새로 생성

    Args:
        name (str): 로거 이름

    Returns:
        logging.Logger: 로거 인스턴스

    Example:
        >>> logger1 = get_logger("MyAgent")
        >>> logger2 = get_logger("MyAgent")  # 같은 인스턴스 반환
        >>> assert logger1 is logger2
    """
    # 이미 핸들러가 있는 로거인지 확인
    existing_logger = logging.getLogger(name)
    if existing_logger.handlers:
        return existing_logger
    else:
        return setup_logger(name)


# ============================================================
# 테스트 코드 (python backend/utils/logger.py 실행 시)
# ============================================================
if __name__ == "__main__":
    """로거 동작 테스트"""

    # ============================================================
    # 1. 기본 로거 생성 및 다양한 레벨 테스트
    # ============================================================
    logger = setup_logger("TestLogger", level="DEBUG")

    logger.debug("디버그 메시지 - 개발 중 상세 정보")
    logger.info("정보 메시지 - 일반 정보")
    logger.warning("경고 메시지 - 주의 필요")
    logger.error("에러 메시지 - 오류 발생")
    logger.critical("치명적 메시지 - 시스템 다운 위험")

    # ============================================================
    # 2. Extra 필드와 함께 로깅
    # ============================================================
    # extra 딕셔너리의 내용이 JSON 필드로 추가됨
    logger.info("작업 완료", extra={
        "duration": 1.23,  # 소요 시간
        "status": "success",  # 상태
        "items_processed": 100  # 처리 항목 수
    })

    # ============================================================
    # 3. 중복 방지 테스트
    # ============================================================
    logger2 = setup_logger("TestLogger")  # 같은 이름
    logger.info("중복 방지 테스트 - 이 메시지는 한 번만 출력되어야 함")
