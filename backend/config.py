"""
중앙 설정 관리 모듈
===================

목적:
    - 애플리케이션 전체에서 사용하는 설정을 중앙에서 관리
    - pydantic-settings를 사용하여 .env 파일에서 환경 변수 자동 로드
    - 타입 안전성 보장 및 기본값 제공

사용법:
    from backend.config import settings
    api_key = settings.openai_api_key
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os
from pathlib import Path

# 프로젝트 루트 경로 계산 (backend/config.py 기준으로 상위 디렉토리)
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스

    Pydantic BaseSettings를 상속받아 환경 변수를 자동으로 로드하고
    타입 검증을 수행합니다.

    Attributes:
        openai_api_key: OpenAI API 키 (필수)
        default_model: 기본 LLM 모델명
        vector_db_path: ChromaDB 저장 경로
        state_db_path: SQLite 데이터베이스 경로
        chunk_size: 텍스트 청킹 크기 (문자 단위)
        similarity_threshold: RAG 유사도 임계값 (0~1)
        ... (기타 설정)
    """

    # ============================================================
    # OpenAI API 설정
    # ============================================================
    openai_api_key: str = Field(
        ...,  # 필수 필드 (None 불가)
        env="OPENAI_API_KEY",
        description="OpenAI API 키"
    )
    default_model: str = Field(
        default="gpt-4o-mini",
        env="DEFAULT_MODEL",
        description="기본 LLM 모델명 (gpt-4o-mini 권장)"
    )

    # ============================================================
    # Google Cloud 설정 (선택적)
    # ============================================================
    google_credentials_path: Optional[str] = Field(
        default=None,
        env="GOOGLE_APPLICATION_CREDENTIALS",
        description="Google Cloud 인증 파일 경로 (OCR Fallback용)"
    )

    # ============================================================
    # 애플리케이션 환경 설정
    # ============================================================
    environment: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="실행 환경 (development/production)"
    )
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="로그 레벨 (DEBUG/INFO/WARNING/ERROR/CRITICAL)"
    )

    # ============================================================
    # 데이터베이스 경로 설정
    # ============================================================
    vector_db_path: str = Field(
        default="data/vector_db",
        env="VECTOR_DB_PATH",
        description="ChromaDB 벡터 데이터베이스 저장 경로"
    )
    state_db_path: str = Field(
        default="data/db/state.db",
        env="STATE_DB_PATH",
        description="SQLite 상태 데이터베이스 파일 경로"
    )
    cache_dir: str = Field(
        default="data/cache",
        env="CACHE_DIR",
        description="캐시 파일 저장 디렉토리"
    )

    # ============================================================
    # 캐시 설정
    # ============================================================
    enable_summary_cache: bool = Field(
        default=True,
        env="ENABLE_SUMMARY_CACHE",
        description="요약 캐싱 활성화 여부 (비용 절감)"
    )
    cache_ttl_hours: int = Field(
        default=24,
        env="CACHE_TTL_HOURS",
        description="캐시 유효 시간 (시간 단위)"
    )

    # ============================================================
    # 비용 모니터링 설정
    # ============================================================
    enable_cost_monitoring: bool = Field(
        default=True,
        env="ENABLE_COST_MONITORING",
        description="비용 모니터링 활성화 여부"
    )
    max_monthly_cost_usd: float = Field(
        default=100.0,
        env="MAX_MONTHLY_COST_USD",
        description="월 최대 비용 한도 (USD)"
    )

    # ============================================================
    # 텍스트 처리 설정
    # ============================================================
    chunk_size: int = Field(
        default=500,
        env="CHUNK_SIZE",
        description="텍스트 청킹 크기 (문자 단위)"
    )
    chunk_overlap: int = Field(
        default=50,
        env="CHUNK_OVERLAP",
        description="청크 간 오버랩 크기 (문자 단위)"
    )
    max_context_tokens: int = Field(
        default=3000,
        env="MAX_CONTEXT_TOKENS",
        description="LLM 컨텍스트 최대 토큰 수"
    )

    # ============================================================
    # RAG (Retrieval-Augmented Generation) 설정
    # ============================================================
    similarity_threshold: float = Field(
        default=0.7,
        env="SIMILARITY_THRESHOLD",
        description="유사도 검색 임계값 (0~1, 높을수록 엄격)"
    )
    top_k_results: int = Field(
        default=5,
        env="TOP_K_RESULTS",
        description="벡터 검색 시 상위 K개 결과 반환"
    )

    # ============================================================
    # 파일 업로드 설정
    # ============================================================
    max_file_size_mb: int = Field(
        default=50,
        env="MAX_FILE_SIZE_MB",
        description="최대 파일 크기 (MB)"
    )
    allowed_extensions: list[str] = Field(
        default=[".pdf"],
        env="ALLOWED_EXTENSIONS",
        description="허용된 파일 확장자 목록"
    )
    upload_dir: str = Field(
        default="data/uploads",
        env="UPLOAD_DIR",
        description="업로드 파일 저장 디렉토리"
    )

    # Pydantic v2 설정 방식 (절대 경로 사용)
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),  # 환경 변수 파일 절대 경로
        env_file_encoding="utf-8",  # 인코딩
        case_sensitive=False,  # 환경 변수명 대소문자 구분 안 함
        extra="ignore"  # .env의 추가 필드 무시 (유연성)
    )


# ============================================================
# 싱글톤 인스턴스 생성
# ============================================================
# 앱 전역에서 사용할 설정 인스턴스
# 모든 모듈에서 이 인스턴스를 import하여 사용
settings = Settings()


def get_settings() -> Settings:
    """
    설정 인스턴스 가져오기

    테스트 및 의존성 주입에서 사용하기 위한 함수입니다.

    Returns:
        Settings: 애플리케이션 설정 인스턴스

    Examples:
        >>> from backend.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.openai_api_key)
    """
    return settings


# ============================================================
# 디렉토리 자동 생성 함수
# ============================================================
def ensure_directories():
    """
    필요한 디렉토리를 자동으로 생성

    앱 시작 시 한 번 실행되어 데이터 저장에 필요한 디렉토리를
    미리 생성합니다.

    생성 디렉토리:
        - vector_db_path: 벡터 DB 저장
        - state_db_path의 부모 디렉토리: SQLite DB 저장
        - cache_dir: 캐시 파일 저장
        - upload_dir: 업로드 파일 저장
    """
    directories = [
        settings.vector_db_path,
        os.path.dirname(settings.state_db_path),  # DB 파일의 부모 디렉토리
        settings.cache_dir,
        settings.upload_dir,
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)  # 이미 있으면 무시


# ============================================================
# 앱 시작 시 디렉토리 생성 실행
# ============================================================
ensure_directories()


# ============================================================
# 테스트 코드 (python backend/config.py 실행 시)
# ============================================================
if __name__ == "__main__":
    """설정 확인용 테스트"""
    print("=== Application Settings ===")
    print(f"Environment: {settings.environment}")
    print(f"OpenAI API Key: {settings.openai_api_key[:20]}...")  # 보안을 위해 일부만 출력
    print(f"Default Model: {settings.default_model}")
    print(f"Vector DB Path: {settings.vector_db_path}")
    print(f"State DB Path: {settings.state_db_path}")
    print(f"Cache Dir: {settings.cache_dir}")
    print(f"Cache Enabled: {settings.enable_summary_cache}")
    print(f"Chunk Size: {settings.chunk_size}")
    print(f"Similarity Threshold: {settings.similarity_threshold}")
