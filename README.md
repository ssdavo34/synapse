# SynapseSimple

PDF 문서 처리 및 벡터 저장 시스템

## 📋 개요
SynapseSimple은 PDF 문서를 업로드하여 텍스트를 추출하고, OpenAI 임베딩으로 변환한 후 ChromaDB에 저장하는 문서 처리 시스템입니다.

## ✨ 주요 기능
- **PDF 업로드 및 저장**: 타임스탬프 기반 파일명으로 저장
- **텍스트 추출**: PyMuPDF를 사용한 고속 텍스트 추출
- **텍스트 청킹**: 500자 단위, 50자 오버랩으로 최적화된 분할
- **임베딩 생성**: OpenAI text-embedding-3-small 모델 사용
- **벡터 DB 저장**: ChromaDB에 세션별 컬렉션으로 저장
- **Streamlit 조회**: 세션 ID 기반 문서 조회 인터페이스

## 🛠 기술 스택
- **Backend**: FastAPI 0.104.1
- **PDF 처리**: PyMuPDF 1.26.5
- **임베딩**: OpenAI API (text-embedding-3-small)
- **벡터 DB**: ChromaDB 0.4.22
- **Frontend**: Streamlit 1.31.0
- **언어**: Python 3.8+

## 📦 설치

### 1. 저장소 클론
```bash
git clone <repository-url>
cd SynapseSimple
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일을 생성하고 OpenAI API 키를 설정:
```
OPENAI_API_KEY=sk-proj-your-key-here
```

## 🚀 실행

### Backend 서버 시작
```bash
python main.py
```
서버가 http://127.0.0.1:8000 에서 실행됩니다.

### Streamlit 앱 시작
```bash
streamlit run app.py
```
브라우저에서 http://localhost:8501 자동 열림

## 📚 API 사용법

### Health Check
```bash
curl http://localhost:8000/api/health
```

### PDF 파일 업로드
```bash
curl -X POST -F "file=@document.pdf" http://localhost:8000/api/upload
```

**응답 예시**:
```json
{
  "status": "success",
  "session_id": "382d04a2-f8ce-4bcb-93cc-8f106afd9832",
  "filename": "document.pdf",
  "text_length": 1234,
  "chunks_count": 6,
  "embeddings_count": 6,
  "embedding_dimension": 1536
}
```

### API 문서
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📖 사용 흐름

1. **PDF 업로드**: FastAPI 엔드포인트로 PDF 파일 업로드
2. **자동 처리**:
   - 파일 저장 (data/uploads/)
   - 텍스트 추출
   - 청킹 (500자 단위)
   - 임베딩 생성
   - ChromaDB 저장
3. **세션 ID 수신**: 응답에서 session_id 확인
4. **Streamlit 조회**: session_id로 문서 내용 조회

## 📁 프로젝트 구조
```
SynapseSimple/
├── main.py              # FastAPI 백엔드
├── app.py               # Streamlit 프론트엔드
├── requirements.txt     # 패키지 의존성
├── .env                 # 환경 변수 (gitignore)
├── .gitignore          # Git 제외 파일
├── README.md           # 이 파일
├── PROJECT_PLAN.md     # 프로젝트 계획서
└── data/
    ├── uploads/        # 업로드된 PDF 파일
    └── vector_db/      # ChromaDB 저장소
```

## ⚙️ 설정

### 청킹 파라미터
- **청크 크기**: 500자
- **오버랩**: 50자
- 위치: `main.py:106-107`

### 임베딩 모델
- **모델**: text-embedding-3-small
- **차원**: 1536
- 위치: `main.py:138`

## 🔍 성능
- 업로드 시간: ~1초
- 텍스트 추출: ~2초
- 청킹: <1초
- 임베딩 생성: ~5초 (6 청크 기준)
- DB 저장: ~1초
- **총 처리 시간**: ~10초

## 🚧 제약사항
- PDF 파일만 지원 (현재)
- 파일 크기 제한: 200MB
- OpenAI API 비용 발생
- 한글/영어 지원

## 📝 추가 문서
- [프로젝트 계획서](PROJECT_PLAN.md): 상세 기술 스펙 및 확장 계획

## 🤝 기여
이슈 및 풀 리퀘스트를 환영합니다!

## 📄 라이선스
MIT License
