# SynapseSimple v2.0 - 개발 가이드

## 🚀 실행 방법

### ✅ 올바른 실행 방법

**항상 프로젝트 루트에서 실행하세요:**

```bash
# 프로젝트 루트로 이동
cd D:\Fastcampus\SynapseSimple

# Python 모듈 실행
python -m backend.config
python -m backend.services.openai_client
python -c "from backend.config import settings; print(settings.project_name)"

# 테스트 실행
pytest backend/tests/

# FastAPI 서버 실행 (향후)
uvicorn backend.main:app --reload
```

### ❌ 피해야 할 실행 방법

```bash
# ❌ backend 디렉토리 안에서 실행하지 마세요
cd D:\Fastcampus\SynapseSimple\backend
python config.py  # ModuleNotFoundError 발생

# ❌ services 디렉토리 안에서 실행하지 마세요
cd D:\Fastcampus\SynapseSimple\backend\services
python openai_client.py  # ModuleNotFoundError 발생
```

## 📁 프로젝트 구조

```
D:\Fastcampus\SynapseSimple\        ← 항상 여기서 실행
├── .env                             ← 환경 변수
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── services/
│   │   ├── openai_client.py
│   │   ├── embedding_service.py
│   │   └── ...
│   ├── utils/
│   │   ├── logger.py
│   │   └── text_processor.py
│   └── tests/
│       └── test_day2_integration.py
├── requirements.txt
└── README.md
```

## 🔧 개발 환경 설정

### 1. 가상 환경 활성화
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일에 다음 내용 추가:
```env
OPENAI_API_KEY=sk-proj-...
DEFAULT_MODEL=gpt-4o-mini
ENVIRONMENT=development
```

### 4. 설정 확인
```bash
python backend/config.py
```

## 🧪 테스트 실행

### 전체 테스트
```bash
pytest backend/tests/ -v
```

### 특정 테스트
```bash
pytest backend/tests/test_day2_integration.py::test_text_processor -v
```

### 커버리지 확인
```bash
pytest backend/tests/ --cov=backend --cov-report=html
```

## 📝 코드 스타일

### Import 순서
```python
# 1. 표준 라이브러리
import os
import sys
from pathlib import Path

# 2. 서드파티 라이브러리
import openai
from pydantic import Field

# 3. 로컬 모듈 (항상 절대 경로)
from backend.config import settings
from backend.utils.logger import setup_logger
from backend.services.openai_client import OpenAIClient
```

### Docstring 스타일
Google Style Docstring 사용

```python
def function_name(param1: str, param2: int) -> bool:
    """
    함수 설명 (한 줄 요약)

    더 자세한 설명 (선택적)

    Args:
        param1: 파라미터 1 설명
        param2: 파라미터 2 설명

    Returns:
        반환값 설명

    Examples:
        >>> function_name("test", 42)
        True
    """
    pass
```

## 🐛 트러블슈팅

### ModuleNotFoundError: No module named 'backend'

**원인**: backend 디렉토리 내부에서 실행했거나 Python path 문제

**해결**:
```bash
# 프로젝트 루트로 이동
cd D:\Fastcampus\SynapseSimple

# 다시 실행
python -m backend.config
```

### ValidationError: openai_api_key field required

**원인**: `.env` 파일이 없거나 OPENAI_API_KEY가 설정되지 않음

**해결**:
```bash
# .env 파일 확인
cat .env

# API 키 추가
echo "OPENAI_API_KEY=sk-proj-..." >> .env
```

### Import 에러 관련

**모든 import는 프로젝트 루트 기준 절대 경로 사용:**
```python
# ✅ 올바른 방법
from backend.config import settings

# ❌ 잘못된 방법
from config import settings  # 상대 경로
from ..config import settings  # 상대 import
```

## 📚 추가 자료

- [Pydantic Settings 문서](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [pytest 문서](https://docs.pytest.org/)

---

**Happy Coding!** 🎉
