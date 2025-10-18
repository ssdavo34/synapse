# SynapseSimple - 프로젝트 계획서

## 1. 프로젝트 개요
PDF 문서를 업로드하여 텍스트를 추출하고, 벡터 임베딩으로 변환하여 ChromaDB에 저장하는 시스템

## 2. 기술 스택
- **Backend**: FastAPI 0.104.1
- **PDF 처리**: PyMuPDF 1.26.5
- **임베딩**: OpenAI text-embedding-3-small
- **벡터 DB**: ChromaDB 0.4.22
- **Frontend**: Streamlit 1.31.0
- **언어**: Python 3.8+

## 3. 시스템 아키텍처

### 3.1 데이터 흐름
```
PDF 업로드 → 파일 저장 → 텍스트 추출 → 청킹 → 임베딩 생성 → ChromaDB 저장
```

### 3.2 디렉토리 구조
```
SynapseSimple/
├── main.py              # FastAPI 백엔드
├── app.py               # Streamlit 프론트엔드
├── requirements.txt     # 패키지 의존성
├── .env                 # 환경 변수 (gitignore)
├── .gitignore          # Git 제외 파일
├── README.md           # 프로젝트 README
├── PROJECT_PLAN.md     # 프로젝트 계획서
└── data/
    ├── uploads/        # 업로드된 PDF 파일
    └── vector_db/      # ChromaDB 저장소
```

## 4. API 엔드포인트

### 4.1 Health Check
```
GET /api/health
```
서버 상태 확인

### 4.2 File Upload
```
POST /api/upload
```
**Request**:
- `file`: PDF 파일 (multipart/form-data)

**Response**:
```json
{
  "status": "success",
  "filename": "document.pdf",
  "saved_filename": "20250118_143022_document.pdf",
  "file_path": "data/uploads/20250118_143022_document.pdf",
  "text_length": 1234,
  "chunks_count": 6,
  "embeddings_count": 6,
  "embedding_dimension": 1536,
  "session_id": "382d04a2-f8ce-4bcb-93cc-8f106afd9832",
  "collection_name": "session_382d04a2-f8ce-4bcb-93cc-8f106afd9832"
}
```

## 5. 개발 단계

### Phase 1: 파일 업로드 ✅
- FastAPI 기본 구조
- 파일 업로드 엔드포인트
- CORS 설정

### Phase 2: 텍스트 추출 ✅
- PyMuPDF 통합
- PDF → 텍스트 변환
- 파일 저장 (타임스탬프)

### Phase 3: 텍스트 청킹 ✅
- 500자 단위 청킹
- 50자 오버랩
- 빈 청크 제거

### Phase 4: 임베딩 생성 ✅
- OpenAI API 연동
- text-embedding-3-small 모델
- 청크별 임베딩 생성

### Phase 5: ChromaDB 저장 ✅
- Persistent 모드
- 세션별 컬렉션
- 메타데이터 저장

### Phase 6: Streamlit 조회 ✅
- 세션 ID 기반 조회
- 청크 내용 표시
- 메타데이터 표시

## 6. 향후 확장 계획

### 단기 (1주)
- [ ] JSON 파일 지원
- [ ] 이미지 파일 지원 (OCR)
- [ ] ZIP 파일 지원

### 중기 (1개월)
- [ ] RAG 기반 질문-답변
- [ ] 문서 요약 생성
- [ ] 검색 기능
- [ ] 다중 파일 업로드

### 장기 (3개월)
- [ ] 사용자 인증
- [ ] 문서 공유 기능
- [ ] API 키 관리
- [ ] 대시보드

## 7. 성능 메트릭
- 업로드 시간: ~1초
- 텍스트 추출: ~2초
- 청킹: <1초
- 임베딩 생성: ~5초 (6 청크)
- DB 저장: ~1초
- 총 처리 시간: ~10초

## 8. 제약사항
- PDF 파일만 지원 (현재)
- 파일 크기 제한: 200MB
- OpenAI API 비용 발생
- 한글/영어 지원

## 9. 환경 변수
`.env` 파일 생성:
```
OPENAI_API_KEY=sk-proj-...
```

## 10. 참고 자료
- FastAPI: https://fastapi.tiangolo.com
- PyMuPDF: https://pymupdf.readthedocs.io
- OpenAI: https://platform.openai.com/docs
- ChromaDB: https://docs.trychroma.com
- Streamlit: https://docs.streamlit.io
