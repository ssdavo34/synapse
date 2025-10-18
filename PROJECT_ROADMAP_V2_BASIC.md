# 📚 SynapseSimple v2.0 기본 - 프로젝트 계획서

## 1. 프로젝트 개요

### 1.1 과제 배경 및 목적

**배경**
- LLM 활용 실무 경험 축적
- 챗봇 서비스 설계 및 구현 역량 강화
- 실제 교육 현장의 문제 해결

**목적**
- RAG 기반 지능형 학습 지원 시스템 구축
- 개인화된 학습 경험 제공
- 효율적인 문서 이해 및 학습 지원

**해결하는 문제**
1. **방대한 문서의 빠른 이해**
   - 긴 PDF 문서를 3줄로 즉시 요약
   - 핵심 개념 자동 추출
   - 난이도 및 학습 시간 예측

2. **학습자 수준별 맞춤 문제 생성**
   - 자동 객관식 퀴즈 생성 (5문항)
   - 즉시 채점 및 레벨 판정
   - 수준별 학습 계획 제공

3. **맞춤형 학습 자료 추천**
   - Wikipedia 기반 관련 자료 검색
   - 주제별 추가 학습 자료 제공

### 1.2 v1.0 완료 현황

**완료된 Phase 1-6**
- ✅ Phase 1: 파일 업로드 (FastAPI)
- ✅ Phase 2: 텍스트 추출 (PyMuPDF)
- ✅ Phase 3: 텍스트 청킹 (500자, 50자 오버랩)
- ✅ Phase 4: 임베딩 생성 (OpenAI text-embedding-3-small)
- ✅ Phase 5: ChromaDB 저장 (Persistent, 세션별)
- ✅ Phase 6: Streamlit 조회 (세션 ID 기반)

**기술 스택**
- Backend: FastAPI 0.104.1
- Vector DB: ChromaDB 0.4.22
- AI: OpenAI API
- Frontend: Streamlit 1.31.0

**성과**
- 처리 시간: ~10초
- 텍스트 추출 성공률: 95%+
- End-to-End 테스트 완료

### 1.3 v2.0 목표

**학원 필수 요구사항 충족**
- ⭐ 문서 즉시 요약 (Map-Reduce)
- ⭐ RAG 기반 Q&A (출처 포함)
- ⭐ 객관식 문제 생성 (5문항)
- ⭐ 자료 추천 (Wikipedia)
- 학습자 진단 (레벨 판정)
- 학습 계획 생성 (3단계)
- 대화 세션 요약

---

## 2. v1.0 vs v2.0 비교

| 기능 | v1.0 | v2.0 기본 | v2.0 확장 |
|------|------|-----------|-----------|
| PDF 처리 | ✅ | ✅ | ✅ |
| 텍스트 추출 | ✅ | ✅ | ✅ |
| 벡터 저장 | ✅ | ✅ | ✅ |
| 📄 문서 요약 | ❌ | ✅ 필수 | 맞춤형 요약 |
| 💬 RAG Q&A | ❌ | ✅ 필수 | 답변없음 처리 |
| ✏️ 객관식 퀴즈 | ❌ | ✅ 필수 | 5문항 고정 |
| 📚 자료 추천 | ❌ | ✅ 필수 | Wikipedia만 |
| 📊 학습 진단 | ❌ | ✅ | 레벨 판정 |
| 📅 학습 계획 | ❌ | ✅ | 3단계 계획 |
| 💾 대화 요약 | ❌ | ✅ | 기본 요약 |
| 단답형/O/X | ❌ | ❌ | ✅ 확장 |
| AI 채점 | ❌ | ❌ | ✅ 확장 |
| Google OCR | ❌ | ❌ | ✅ 선택 |
| 비용 모니터링 | ❌ | ❌ | ✅ 확장 |

**v2.0 기본 = 학원 필수 요구사항만**

---

## 3. 핵심 기능 명세 (기본)

### 3.1 ⭐ 문서 즉시 요약 (필수)

**목적**: 긴 PDF 문서를 빠르게 이해

**입력**
- PDF 텍스트 (전체)

**처리 로직**
1. 토큰 수 계산 (tiktoken)
2. **< 3000 토큰**: 직접 요약 (단일 LLM 호출)
3. **≥ 3000 토큰**: Map-Reduce 알고리즘
   - Map: 각 청크 개별 요약
   - Reduce: 통합 요약 생성
4. 캐싱 시스템 (동일 문서 재요약 방지)
   - 파일 해시 기반
   - 90% API 비용 절감

**출력 형식**
```json
{
  "tldr": [
    "핵심 내용 1",
    "핵심 내용 2",
    "핵심 내용 3"
  ],
  "main_topic": "문서의 주요 주제",
  "key_concepts": [
    "개념1",
    "개념2",
    "개념3",
    "개념4",
    "개념5"
  ],
  "difficulty_level": "beginner|intermediate|advanced",
  "estimated_time_minutes": 120,
  "quality_score": 0.85
}
```

**품질 평가**
- 완성도: 3줄 요약 존재
- 개념 수: 3-7개
- 난이도: 명확한 분류
- Score: 0.0-1.0

**구현**
- `SummaryAgent.summarize_document()`
- `SummaryCache` (Redis-like dict)

**성능 목표**
- 처리 시간: <10초
- 품질 점수: ≥0.7
- 캐싱 적중률: 90%+

---

### 3.2 ⭐ RAG 기반 Q&A (필수)

**목적**: 문서 내용에 대한 정확한 답변

**입력**
- 사용자 질문 (텍스트)
- 세션 ID

**처리 플로우**
1. 질문 임베딩 생성 (OpenAI)
2. ChromaDB 유사도 검색
   - Top-K: 5개 청크
3. 유사도 필터링
   - Threshold: 0.7
   - 0.7 미만: 모두 제외
4. LLM 답변 생성
   - 검색된 청크 + 질문
   - 출처 포함 답변
5. Q&A 기록 저장 (SQLite)

**출력 형식**
```json
{
  "answer": "답변 내용...",
  "sources": [
    {
      "chunk_id": 0,
      "text": "관련 텍스트...",
      "similarity": 0.85
    },
    {
      "chunk_id": 3,
      "text": "관련 텍스트...",
      "similarity": 0.78
    }
  ],
  "has_sources": true
}
```

**구현**
- `RAGService.answer_question()`
- `ExecutionAgent` (답변 생성)

**제약사항**
- 답변 없음 처리는 v2.0 확장에서
- 기본: 검색 실패 시 "정보 없음" 메시지

**성능 목표**
- 응답 시간: <5초
- 정확도: 출처 기반 답변

---

### 3.3 ⭐ 객관식 문제 생성 (필수)

**목적**: 학습 이해도 평가

**입력**
- 세션 ID (문서 요약 정보)

**처리 로직**
1. 문서 요약의 `key_concepts` 활용
2. ChromaDB에서 대표 청크 샘플링
   - 개념당 1-2개 청크
3. LLM 문제 생성
   - 5문항 (4지선다)
   - 정답 1개
   - 오답 3개 (그럴듯한)
   - 해설 포함

**출력 형식**
```json
{
  "questions": [
    {
      "id": 1,
      "question": "토마토 재배에서 가장 중요한 요소는?",
      "options": [
        "물주기",
        "햇빛",
        "온도",
        "토양"
      ],
      "correct_answer": 1,
      "explanation": "토마토는 햇빛을 많이 필요로 하는 작물입니다..."
    }
  ],
  "total_questions": 5
}
```

**채점**
- 자동 채점 (인덱스 비교)
- 점수: 0-100 (20점 단위)

**구현**
- `DiagnosisAgent.generate_quiz()`
- 간소화된 버전 (객관식만)

**제약사항**
- 5문항 고정
- 객관식만 지원
- 난이도 조절 없음

**성능 목표**
- 생성 시간: <8초
- 문제 품질: 명확한 정답

---

### 3.4 ⭐ 자료 추천 (필수)

**목적**: 추가 학습 자료 제공

**입력**
- 주제 키워드 (문서의 main_topic)

**처리**
1. Wikipedia API 호출
2. 검색어: 주제 키워드
3. 상위 3개 문서 선택
4. 요약 추출 (첫 3문장)

**출력 형식**
```json
{
  "resources": [
    {
      "title": "토마토",
      "summary": "토마토는 가지과의...",
      "url": "https://ko.wikipedia.org/wiki/토마토"
    }
  ],
  "count": 3
}
```

**구현**
- `WikipediaService.search()`
- Wikipedia-API 라이브러리 사용

**제약사항**
- Wikipedia만 지원
- 3개 고정
- 한국어 우선

**성능 목표**
- 검색 시간: <3초

---

### 3.5 학습자 진단 (필수)

**목적**: 학습자 수준 파악

**입력**
- 퀴즈 결과 (5문항 답안)

**처리**
1. 정답 비교
2. 점수 계산
   - 맞은 개수 × 20
3. 레벨 판정
   - 0-40점: beginner
   - 41-70점: intermediate
   - 71-100점: advanced

**출력 형식**
```json
{
  "score": 80,
  "level": "advanced",
  "correct_count": 4,
  "total_count": 5,
  "feedback": "우수한 이해도를 보입니다!"
}
```

**구현**
- `DiagnosisAgent.evaluate_quiz()`

**성능 목표**
- 즉시 결과 (< 1초)

---

### 3.6 학습 계획 생성 (필수)

**목적**: 맞춤형 학습 로드맵 제공

**입력**
- 학습자 프로필 (레벨)
- 문서 요약 (key_concepts, difficulty)

**처리 로직**
1. 레벨별 템플릿 선택
2. LLM으로 3단계 계획 생성
   - 기초: 핵심 개념 이해
   - 심화: 응용 및 실습
   - 응용: 고급 주제 탐구

**출력 형식**
```json
{
  "plan": {
    "phase1": {
      "title": "기초 단계",
      "duration": "1-2주",
      "topics": ["토마토 품종", "기본 재배 환경"],
      "activities": ["문서 정독", "기본 퀴즈"]
    },
    "phase2": {
      "title": "심화 단계",
      "duration": "2-3주",
      "topics": ["병충해 관리", "수확 시기"],
      "activities": ["실습 문제", "사례 연구"]
    },
    "phase3": {
      "title": "응용 단계",
      "duration": "1주",
      "topics": ["스마트팜 적용", "수익성 분석"],
      "activities": ["프로젝트", "심화 토론"]
    }
  }
}
```

**구현**
- `PlanningAgent.create_plan()`

**성능 목표**
- 생성 시간: <5초

---

### 3.7 대화 세션 요약 (필수)

**목적**: 학습 내용 정리

**트리거**
- 사용자 "지금까지 요약" 버튼 클릭

**입력**
- Q&A 대화 기록 (SQLite)

**처리**
1. 대화 기록 로드
2. LLM으로 요약 생성
   - 주요 학습 내용
   - 새로운 개념
   - 복습 포인트

**출력 형식**
```json
{
  "key_learnings": [
    "토마토는 햇빛이 중요하다",
    "물주기는 일주일에 2-3회"
  ],
  "new_concepts": [
    "적심",
    "곁순제거"
  ],
  "review_points": [
    "병충해 예방법 복습",
    "수확 시기 재확인"
  ],
  "total_qa_count": 5
}
```

**구현**
- `SummaryAgent.summarize_conversation()`

**성능 목표**
- 요약 시간: <5초

---

## 4. 기술 스택 (v2.0 기본)

### v1.0 유지
```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pymupdf==1.26.5
openai==1.54.0
python-dotenv==1.0.1
chromadb==0.4.22
streamlit==1.31.0
```

### v2.0 추가
```
aiosqlite==0.19.0      # 비동기 SQLite
tenacity==8.2.3        # 재시도 로직
tiktoken==0.5.1        # 토큰 계산
wikipedia-api==0.6.0   # Wikipedia 검색
```

### v2.0 확장으로 이동 (제외)
```
# 이번 단계에서는 제외
google-cloud-vision   # Google OCR
konlpy                # 한국어 형태소 분석 (단답형용)
redis                 # 고급 캐싱
prometheus-client     # 모니터링
```

### 전체 requirements.txt
```
# Core
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6

# AI & ML
openai==1.54.0
chromadb==0.4.22

# PDF Processing
pymupdf==1.26.5

# Database
aiosqlite==0.19.0

# Utilities
python-dotenv==1.0.1
tenacity==8.2.3
tiktoken==0.5.1
wikipedia-api==0.6.0

# Frontend
streamlit==1.31.0
```

---

## 5. 데이터 모델 (SQLite)

### 테이블 설계 (4개)

```sql
-- 1. 학습 세션
CREATE TABLE learning_sessions (
    session_id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 문서 요약
CREATE TABLE document_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    tldr TEXT NOT NULL,
    main_topic TEXT NOT NULL,
    key_concepts TEXT NOT NULL,  -- JSON array
    difficulty_level TEXT NOT NULL,
    estimated_time_minutes INTEGER,
    quality_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- 3. Q&A 기록
CREATE TABLE qa_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources TEXT,  -- JSON array
    similarity_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- 4. 학습자 프로필
CREATE TABLE learner_profiles (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    score INTEGER NOT NULL,
    level TEXT NOT NULL,  -- beginner|intermediate|advanced
    quiz_results TEXT NOT NULL,  -- JSON array
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);
```

### 인덱스
```sql
CREATE INDEX idx_session_id ON qa_history(session_id);
CREATE INDEX idx_session_created ON learning_sessions(created_at);
CREATE INDEX idx_file_hash ON learning_sessions(file_hash);
```

### 제외된 테이블 (확장에서)
- `conversation_summaries` (대화 요약 별도 저장)
- `api_usage_logs` (비용 모니터링)
- `user_preferences` (사용자 설정)

---

## 6. API 엔드포인트 (기본 8개)

### 6.1 파일 업로드 + 자동 요약
```
POST /api/upload
```

**Request**
```
Content-Type: multipart/form-data
file: PDF 파일
```

**Response**
```json
{
  "session_id": "uuid",
  "file_name": "토마토재배.pdf",
  "summary": {
    "tldr": [...],
    "main_topic": "...",
    "key_concepts": [...],
    "difficulty_level": "intermediate",
    "quality_score": 0.85
  },
  "chunks_count": 12,
  "processing_time_seconds": 8.5
}
```

---

### 6.2 문서 요약 조회
```
GET /api/summary/document/{session_id}
```

**Response**
```json
{
  "summary": {
    "tldr": [...],
    "main_topic": "...",
    "key_concepts": [...]
  }
}
```

---

### 6.3 대화 요약 생성
```
POST /api/summary/conversation
```

**Request**
```json
{
  "session_id": "uuid"
}
```

**Response**
```json
{
  "key_learnings": [...],
  "new_concepts": [...],
  "review_points": [...]
}
```

---

### 6.4 객관식 퀴즈 생성
```
POST /api/diagnosis/{session_id}
```

**Response**
```json
{
  "questions": [
    {
      "id": 1,
      "question": "...",
      "options": [...],
      "correct_answer": 1,
      "explanation": "..."
    }
  ]
}
```

---

### 6.5 퀴즈 제출 및 채점
```
POST /api/diagnosis/submit
```

**Request**
```json
{
  "session_id": "uuid",
  "answers": [0, 1, 2, 1, 3]
}
```

**Response**
```json
{
  "score": 80,
  "level": "advanced",
  "feedback": "..."
}
```

---

### 6.6 RAG Q&A
```
POST /api/ask
```

**Request**
```json
{
  "session_id": "uuid",
  "question": "토마토 물주기 주기는?"
}
```

**Response**
```json
{
  "answer": "...",
  "sources": [...]
}
```

---

### 6.7 학습 계획 생성
```
POST /api/plan/{session_id}
```

**Response**
```json
{
  "plan": {
    "phase1": {...},
    "phase2": {...},
    "phase3": {...}
  }
}
```

---

### 6.8 헬스체크
```
GET /api/health
```

**Response**
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

---

### 제외된 API (확장에서)
- `POST /api/quiz/configure` (퀴즈 설정)
- `GET /api/monitoring/cost` (비용 모니터링)
- `POST /api/summary/custom` (맞춤형 요약)

---

## 7. 에이전트 시스템 (3개)

### 7.1 SummaryAgent ⭐

**책임**
- 문서 요약 (Map-Reduce)
- 대화 요약
- 품질 평가

**주요 메서드**
```python
class SummaryAgent:
    async def summarize_document(
        self,
        text: str,
        use_cache: bool = True
    ) -> DocumentSummary:
        """문서 요약 (Map-Reduce)"""

    async def summarize_conversation(
        self,
        qa_history: List[QA]
    ) -> ConversationSummary:
        """대화 요약"""

    def calculate_quality_score(
        self,
        summary: dict
    ) -> float:
        """품질 점수 계산"""
```

**핵심 로직**
- Map-Reduce 알고리즘
- 캐싱 시스템 (파일 해시)
- 품질 평가 (완성도 체크)

---

### 7.2 DiagnosisAgent

**책임**
- 객관식 5문항 생성
- 자동 채점
- 레벨 판정

**주요 메서드**
```python
class DiagnosisAgent:
    async def generate_quiz(
        self,
        session_id: str
    ) -> Quiz:
        """객관식 5문항 생성"""

    def evaluate_quiz(
        self,
        answers: List[int],
        correct_answers: List[int]
    ) -> Evaluation:
        """자동 채점 + 레벨 판정"""
```

**간소화**
- 객관식만 지원
- 5문항 고정
- 간단한 레벨 판정

---

### 7.3 PlanningAgent

**책임**
- 학습 계획 생성 (3단계)

**주요 메서드**
```python
class PlanningAgent:
    async def create_plan(
        self,
        profile: LearnerProfile,
        summary: DocumentSummary
    ) -> LearningPlan:
        """3단계 학습 계획"""
```

**계획 구조**
- Phase 1: 기초
- Phase 2: 심화
- Phase 3: 응용

---

### 제외된 에이전트 (확장에서)
- `EvaluationAgent` (AI 채점)
- `CustomizationAgent` (맞춤형 요약)

### 서비스 레이어 (에이전트 아님)
- `RAGService` (검색 + 답변)
- `EmbeddingService` (임베딩 생성)
- `OCRService` (텍스트 추출)
- `WikipediaService` (자료 검색)

---

## 8. 개발 로드맵 (4일)

### 📅 Day 1: 백엔드 코어 (10시간)

**Phase 1: 환경 설정 (2시간)**
- ✅ requirements.txt 업데이트
- ✅ config.py 작성
  - OpenAI API 키
  - DB 경로
  - 캐시 설정
- ✅ logger.py 작성
  - 구조화 로깅
  - 파일 + 콘솔

**Phase 2: 파일 처리 (2시간)**
- ✅ FileValidator
  - PDF 확장자 체크
  - 파일 크기 제한 (200MB)
  - MIME 타입 검증
- ✅ OCRService
  - PyMuPDF 텍스트 추출
  - 페이지별 처리
  - 에러 핸들링

**Phase 3: SummaryAgent ⭐ (3시간)**
- ✅ 캐싱 시스템
  - 파일 해시 계산
  - 메모리 캐시 (dict)
- ✅ Map-Reduce 알고리즘
  - 토큰 수 계산 (tiktoken)
  - 청크별 요약 (Map)
  - 통합 요약 (Reduce)
- ✅ 품질 평가
  - 완성도 체크
  - 점수 계산 (0-1)

**Phase 4: RAG + DB (3시간)**
- ✅ RAGService
  - 임베딩 검색
  - 유사도 필터링 (0.7)
  - 답변 생성
- ✅ SQLite 스키마
  - 4개 테이블 생성
  - 인덱스 추가
- ✅ StateDB 클래스
  - CRUD 메서드
  - 비동기 처리

---

### 📅 Day 2: 에이전트 + API (10시간)

**Phase 1: 나머지 에이전트 (3시간)**
- ✅ DiagnosisAgent
  - 객관식 5문항 생성
  - LLM 프롬프트 최적화
  - 자동 채점 로직
  - 레벨 판정 (3단계)
- ✅ PlanningAgent
  - 3단계 계획 생성
  - 레벨별 템플릿
  - LLM 호출

**Phase 2: FastAPI (4시간)**
- ✅ 8개 엔드포인트 구현
  - `/api/upload`
  - `/api/summary/*`
  - `/api/diagnosis/*`
  - `/api/ask`
  - `/api/plan/*`
  - `/api/health`
- ✅ Pydantic 모델
  - Request/Response 스키마
  - 유효성 검증
- ✅ 에러 핸들링
  - 커스텀 예외
  - 에러 응답 표준화

**Phase 3: Wikipedia (2시간)**
- ✅ WikipediaService
  - 검색 API 호출
  - 상위 3개 선택
  - 요약 추출
- ✅ 테스트
  - 검색 정확도
  - 응답 시간

**Phase 4: 통합 테스트 (1시간)**
- ✅ End-to-End 플로우
- ✅ 에러 케이스
- ✅ 성능 측정

---

### 📅 Day 3: UI (8시간)

**Phase 1: Streamlit 기본 (4시간)**
- ✅ 홈 페이지
  - 파일 업로드 위젯
  - 업로드 후 자동 요약 표시
- ✅ 요약 카드 컴포넌트 ⭐
  - TL;DR 3줄
  - 핵심 개념 (태그)
  - 난이도 배지
  - 예상 학습 시간
- ✅ 진단 퀴즈 페이지
  - 5문항 객관식
  - 라디오 버튼
  - 제출 버튼
  - 결과 표시 (점수 + 레벨)

**Phase 2: Q&A + 대시보드 (3시간)**
- ✅ 채팅 페이지
  - 질문 입력창
  - 답변 표시 (출처 포함)
  - 대화 기록
- ✅ 대화 요약 버튼
  - "지금까지 요약" 버튼
  - 요약 결과 표시
- ✅ 학습 계획 페이지
  - 3단계 계획 표시
  - 진행 상황 체크리스트

**Phase 3: 사이드바 (1시간)**
- ✅ 세션 선택
- ✅ 페이지 네비게이션
- ✅ 자료 추천 (Wikipedia)

---

### 📅 Day 4: 테스트 + 문서 (4시간)

**Phase 1: E2E 테스트 (2시간)**
- ✅ 전체 플로우 시연
  1. PDF 업로드 (토마토 재배)
  2. 자동 요약 확인
  3. 퀴즈 수행 (5문항)
  4. Q&A 5회
  5. 대화 요약
  6. 학습 계획 확인
  7. 자료 추천 확인
- ✅ 성능 측정
  - 각 단계 시간
  - 총 처리 시간
  - API 호출 횟수

**Phase 2: 문서화 (2시간)**
- ✅ README.md 업데이트
  - v2.0 기능 추가
  - 사용 가이드
  - API 문서 링크
- ✅ API 문서 (Swagger)
  - 자동 생성
  - 예시 추가
- ✅ 시연 준비
  - 스크립트 작성
  - 테스트 데이터 준비

---

## 9. 성공 지표 (KPI)

### 학원 요구사항 달성

**문서 요약 ⭐**
- ✅ 처리 시간: <10초
- ✅ 품질 점수: ≥0.7
- ✅ 캐싱 적중률: 90%+

**Q&A ⭐**
- ✅ 응답 시간: <5초
- ✅ 출처 포함: 100%
- ✅ 정확도: 관련 청크 검색

**문제 생성 ⭐**
- ✅ 생성 시간: <8초
- ✅ 5문항 생성: 100%
- ✅ 자동 채점: 즉시

**자료 추천 ⭐**
- ✅ 검색 시간: <3초
- ✅ Wikipedia 제공: 3개

### 기술 성능

**처리 시간**
- 전체 플로우: <20초
- 파일 업로드 + 요약: <10초
- 퀴즈 생성: <8초
- Q&A 응답: <5초

**캐싱 효과**
- API 호출 감소: 90%
- 비용 절감: $18/월 → $2/월

**정확도**
- 텍스트 추출: 95%+
- 유사도 검색: Top-5 정확도

---

## 10. 비용 예산 (기본)

### MVP (100명/월 기준)

**임베딩**
- 모델: text-embedding-3-small
- 문서당 평균: 20 청크
- 총 청크: 2,000
- 비용: $0.0001 / 1K 토큰 × 1M 토큰 = **$2**

**요약 (캐싱 90%)**
- 모델: GPT-4o-mini
- 실제 호출: 10회 (90% 캐싱)
- 비용: $0.60 / 1M 입력 × 10M = **$6**

**Q&A**
- 사용자당 10회
- 총: 1,000회
- 비용: $0.60 / 1M × 13.3M = **$8**

**문제 생성**
- 사용자당 1회
- 총: 100회
- 비용: $0.60 / 1M × 5M = **$3**

**Wikipedia**
- 무료

**총 비용: ~$19/월**
**사용자당: $0.19**

### 확장 시 (1,000명/월)
- 임베딩: $20
- 요약: $60
- Q&A: $80
- 문제: $30
- **총: ~$190/월**
- **사용자당: $0.19 (동일)**

---

## 11. 프로젝트 구조 (간소화)

```
SynapseSimple/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── summary_agent.py      # ⭐ 문서/대화 요약
│   │   ├── diagnosis_agent.py    # 퀴즈 생성 + 채점
│   │   └── planning_agent.py     # 학습 계획
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py        # PyMuPDF만
│   │   ├── embedding_service.py  # OpenAI 임베딩
│   │   ├── rag_service.py        # 검색 + 답변
│   │   └── wikipedia_service.py  # 자료 추천
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── schema.sql            # 테이블 스키마
│   │   └── state_db.py           # SQLite 클래스
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py           # Pydantic Request
│   │   └── responses.py          # Pydantic Response
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── text_processor.py    # 텍스트 처리
│   │   ├── summary_cache.py     # ⭐ 캐싱 시스템
│   │   ├── file_validator.py    # 파일 검증
│   │   └── token_counter.py     # tiktoken
│   │
│   ├── config.py                 # 설정
│   ├── logger.py                 # 로깅
│   └── main.py                   # FastAPI 앱
│
├── frontend/
│   ├── pages/
│   │   ├── 1_📁_Home.py          # 업로드 + 요약
│   │   ├── 2_✏️_Diagnosis.py     # 객관식 퀴즈
│   │   ├── 3_💬_QA.py            # 채팅
│   │   └── 4_📅_Plan.py          # 학습 계획
│   │
│   ├── components/
│   │   ├── __init__.py
│   │   ├── summary_card.py      # ⭐ 요약 카드
│   │   ├── quiz_widget.py       # 퀴즈 위젯
│   │   └── chat_widget.py       # 채팅 위젯
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── api_client.py        # API 호출
│   │
│   └── app.py                    # Streamlit 메인
│
├── prompts/
│   ├── __init__.py
│   ├── summary_prompts.py       # 요약 프롬프트
│   ├── diagnosis_prompts.py     # 퀴즈 프롬프트
│   ├── planning_prompts.py      # 계획 프롬프트
│   └── qa_prompts.py            # Q&A 프롬프트
│
├── tests/
│   ├── test_agents.py
│   ├── test_services.py
│   ├── test_api.py
│   └── test_e2e.py
│
├── data/
│   ├── uploads/                 # PDF 파일
│   ├── vector_db/               # ChromaDB
│   └── state.db                 # SQLite
│
├── docs/
│   ├── API.md                   # API 문서
│   └── DEMO.md                  # 시연 시나리오
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── PROJECT_PLAN.md              # v1.0 계획
├── PROJECT_COMPLETE_V1.md       # v1.0 완료
└── PROJECT_ROADMAP_V2_BASIC.md  # 본 문서
```

---

## 12. 시연 시나리오 (학원 발표)

### 🎬 시나리오: 농작물 학습 지원 시스템

**준비물**
- PDF: "토마토 재배 가이드" (20페이지)
- 브라우저 2개
  - Tab 1: FastAPI (http://localhost:8000/docs)
  - Tab 2: Streamlit (http://localhost:8501)

---

### 🎯 Step 1: 자료 업로드 (2분)

**행동**
1. Streamlit 홈 화면 접속
2. "토마토재배.pdf" 업로드
3. 자동 처리 시작 (로딩)

**결과 화면**
```
✅ 업로드 완료!

📄 문서 요약
━━━━━━━━━━━━━━━━━━━━━━
📌 TL;DR:
• 토마토는 햇빛과 물 관리가 핵심
• 병충해 예방을 위한 정기 점검 필요
• 수확 시기는 색깔과 단단함으로 판단

🎯 주요 개념:
#토마토품종 #재배환경 #물주기 #병충해 #수확

📊 난이도: Intermediate
⏱️ 예상 학습 시간: 120분
✨ 품질 점수: 0.87
━━━━━━━━━━━━━━━━━━━━━━
```

**설명**
- "문서를 업로드하면 자동으로 핵심 내용을 3줄로 요약합니다."
- "5개의 핵심 개념을 추출하여 학습 포인트를 제시합니다."
- "난이도와 예상 학습 시간도 자동 계산됩니다."

---

### 🎯 Step 2: 학습 진단 - 퀴즈 (3분)

**행동**
1. "진단 퀴즈" 페이지 이동
2. "퀴즈 생성" 버튼 클릭
3. 5문항 표시

**화면**
```
✏️ 학습 진단 퀴즈 (5문항)

━━━━━━━━━━━━━━━━━━━━━━
문제 1. 토마토 재배에서 가장 중요한 요소는?

○ A. 물주기
● B. 햇빛
○ C. 온도
○ D. 토양

━━━━━━━━━━━━━━━━━━━━━━
문제 2. 토마토 물주기 주기는?

○ A. 매일
● B. 2-3일에 1회
○ C. 일주일에 1회
○ D. 10일에 1회

━━━━━━━━━━━━━━━━━━━━━━
... (3개 더)

[제출하기]
```

**행동**
- 5문항 답변 선택 (의도적으로 1개 틀림)
- "제출하기" 버튼

**결과 화면**
```
✅ 채점 완료!

━━━━━━━━━━━━━━━━━━━━━━
🎯 점수: 80점 (4/5)
📊 레벨: Advanced

💬 피드백:
우수한 이해도를 보입니다!
심화 학습으로 넘어가시면 됩니다.
━━━━━━━━━━━━━━━━━━━━━━
```

**설명**
- "문서 내용을 바탕으로 객관식 5문항을 자동 생성합니다."
- "즉시 자동 채점하여 점수와 레벨을 판정합니다."
- "레벨에 따라 맞춤형 학습 계획을 제공합니다."

---

### 🎯 Step 3: Q&A 대화 (4분)

**행동**
1. "Q&A" 페이지 이동
2. 5개 질문 입력

**대화 예시**
```
💬 질문 1:
"토마토 물주기 주기는?"

🤖 답변:
토마토는 2-3일에 1회 물을 주는 것이 적절합니다.
토양이 건조하지 않도록 유지하되, 과습을 피해야 합니다.

📚 출처:
[Chunk 3] 유사도: 0.85
"토마토는 물 관리가 중요하며, 2-3일에 한 번
충분히 물을 주는 것이 좋습니다..."

━━━━━━━━━━━━━━━━━━━━━━

💬 질문 2:
"병충해는 어떻게 예방하나요?"

🤖 답변:
정기적인 잎 점검과 통풍이 중요합니다.
초기 발견 시 유기농 방제제를 사용합니다.

📚 출처:
[Chunk 7] 유사도: 0.81
...

━━━━━━━━━━━━━━━━━━━━━━

... (3개 질문 더)
```

**행동**
- "지금까지 요약" 버튼 클릭

**대화 요약 화면**
```
💾 대화 세션 요약

━━━━━━━━━━━━━━━━━━━━━━
📖 주요 학습 내용:
• 토마토 물주기는 2-3일 간격
• 병충해 예방은 정기 점검이 핵심
• 수확 시기는 색깔 변화로 판단

🆕 새로운 개념:
• 적심 (곁순 제거)
• 유기농 방제
• 통풍 관리

📝 복습 포인트:
• 병충해 초기 증상 재확인
• 수확 시기 판단 기준 정리
━━━━━━━━━━━━━━━━━━━━━━
```

**설명**
- "문서 내용을 검색하여 정확한 답변을 제공합니다."
- "모든 답변에 출처(청크)와 유사도를 함께 표시합니다."
- "대화 세션을 요약하여 학습 내용을 정리합니다."

---

### 🎯 Step 4: 학습 계획 (2분)

**행동**
1. "학습 계획" 페이지 이동
2. "계획 생성" 버튼

**화면**
```
📅 맞춤형 학습 계획

━━━━━━━━━━━━━━━━━━━━━━
📚 기초 단계 (1-2주)
━━━━━━━━━━━━━━━━━━━━━━
🎯 학습 주제:
• 토마토 품종 이해
• 기본 재배 환경 조성
• 물주기 및 비료

📝 활동:
☐ 문서 정독
☐ 기본 퀴즈 수행
☐ 재배 환경 체크리스트 작성

━━━━━━━━━━━━━━━━━━━━━━
🔬 심화 단계 (2-3주)
━━━━━━━━━━━━━━━━━━━━━━
🎯 학습 주제:
• 병충해 식별 및 관리
• 수확 시기 판단
• 적심 및 곁순 제거

📝 활동:
☐ 실습 문제 풀이
☐ 사례 연구
☐ 실전 재배 계획 수립

━━━━━━━━━━━━━━━━━━━━━━
🚀 응용 단계 (1주)
━━━━━━━━━━━━━━━━━━━━━━
🎯 학습 주제:
• 스마트팜 기술 적용
• 수익성 분석
• 품질 개선 전략

📝 활동:
☐ 미니 프로젝트
☐ 심화 토론
☐ 전문가 자료 학습
━━━━━━━━━━━━━━━━━━━━━━
```

**설명**
- "레벨에 맞는 3단계 학습 계획을 자동 생성합니다."
- "각 단계별 주제, 활동, 기간을 제시합니다."

---

### 🎯 Step 5: 추가 자료 추천 (1분)

**행동**
1. 사이드바 "자료 추천" 클릭

**화면**
```
📚 추천 학습 자료 (Wikipedia)

━━━━━━━━━━━━━━━━━━━━━━
1. 토마토
토마토는 가지과의 한해살이 또는
여러해살이 식물로...

🔗 https://ko.wikipedia.org/wiki/토마토

━━━━━━━━━━━━━━━━━━━━━━
2. 스마트팜
스마트팜은 정보통신기술(ICT)을
온실·축사 등에 접목하여...

🔗 https://ko.wikipedia.org/wiki/스마트팜

━━━━━━━━━━━━━━━━━━━━━━
3. 유기농업
유기농업은 화학비료와 농약을
사용하지 않고...

🔗 https://ko.wikipedia.org/wiki/유기농업
━━━━━━━━━━━━━━━━━━━━━━
```

**설명**
- "주제에 맞는 Wikipedia 자료를 추천합니다."
- "추가 학습을 위한 신뢰할 수 있는 자료를 제공합니다."

---

### 📊 시연 요약 (30초)

**완료된 플로우**
1. ✅ PDF 업로드 → 즉시 요약
2. ✅ 객관식 퀴즈 → 자동 채점
3. ✅ Q&A 5회 → 출처 포함 답변
4. ✅ 대화 요약 → 학습 정리
5. ✅ 학습 계획 → 3단계 맞춤형
6. ✅ 자료 추천 → Wikipedia 3개

**처리 시간**
- 전체: ~20초
- 요약: ~8초
- 퀴즈: ~8초
- Q&A: ~4초/회

**학원 요구사항 충족**
- ✅ 문서 요약
- ✅ Q&A
- ✅ 문제 생성
- ✅ 자료 추천
- ✅ 학습 진단
- ✅ 학습 계획

---

## 13. 제한사항 (명확히)

### v2.0 기본에 포함되지 않는 기능

**퀴즈 관련**
- ❌ 단답형 문제
- ❌ O/X 문제
- ❌ AI 기반 단답형 채점
- ❌ 퀴즈 설정 변경 (문항 수, 난이도)
- ❌ 문제 은행 시스템

**Q&A 관련**
- ❌ Perplexity 스타일 답변없음 처리
- ❌ 다중 모델 비교
- ❌ 질문 추천 기능

**요약 관련**
- ❌ 맞춤형 요약 (길이, 스타일)
- ❌ 다국어 요약
- ❌ 요약 이력 관리

**OCR 관련**
- ❌ Google Cloud Vision OCR
- ❌ 이미지 PDF 처리
- ❌ 표/그림 추출

**모니터링**
- ❌ 비용 모니터링 API
- ❌ 사용량 대시보드
- ❌ 성능 프로파일링

**보안**
- ❌ 사용자 인증
- ❌ API 키 관리
- ❌ 파일 암호화

**고급 기능**
- ❌ 다중 파일 비교
- ❌ 문서 버전 관리
- ❌ 협업 기능

---

### 제한 이유

**개발 기간**
- 4일 집중 개발
- 핵심 기능 우선

**학원 요구사항**
- 필수 기능만 포함
- 확장은 다음 단계

**복잡도 최소화**
- 안정적인 MVP
- 유지보수 용이

**비용 효율**
- 불필요한 API 호출 제거
- 최소 비용으로 최대 효과

---

### 확장 계획

**v2.0 고급 (확장)**
- 다양한 퀴즈 유형
- AI 채점
- Perplexity 스타일 Q&A
- Google OCR
- 비용 모니터링

**v3.0 (장기)**
- 사용자 인증
- 협업 기능
- 다국어 지원
- 모바일 앱

---

## 14. v2.0 고급 (확장 예고)

### 다음 단계 기능

**🎯 다양한 퀴즈 유형**
- 단답형 문제 생성
- O/X 문제 생성
- 서술형 문제 (AI 채점)
- 난이도별 문제 생성
- 문제 은행 시스템

**🤖 AI 기반 채점**
- 단답형 키워드 매칭
- 유사도 기반 채점
- 부분 점수 지원
- 채점 피드백 생성

**🔍 Perplexity 스타일 Q&A**
- 답변 없음 명확히 표시
- 대안 질문 추천
- 외부 검색 연동
- 다중 소스 종합

**✨ 맞춤형 요약**
- 요약 길이 조절 (짧게/길게)
- 스타일 선택 (학술적/대화체)
- 특정 부분 집중 요약
- 요약 이력 관리

**📸 Google OCR**
- 이미지 PDF 처리
- 표/그림 추출
- 손글씨 인식
- 다국어 OCR

**📊 비용 모니터링**
- API 사용량 추적
- 비용 대시보드
- 예산 알림
- 최적화 제안

**🔐 고급 보안**
- 사용자 인증 (JWT)
- API 키 관리
- 파일 암호화
- 접근 제어

---

### 확장 로드맵

**Phase 1 (1주)**
- 단답형/O/X 문제
- AI 채점 기본

**Phase 2 (2주)**
- Perplexity Q&A
- 맞춤형 요약

**Phase 3 (1주)**
- Google OCR
- 비용 모니터링

**Phase 4 (2주)**
- 사용자 인증
- 고급 보안

---

### 자세한 내용

**다음 문서 참고**
- `PROJECT_ROADMAP_V2_ADVANCED.md` (작성 예정)

---

## 15. 참고 자료

### 프로젝트 문서
- **v1.0 완료 보고서**: `PROJECT_COMPLETE_V1.md`
- **v1.0 계획서**: `PROJECT_PLAN.md`
- **최초 계획**: 시냅스 개발 계획서 v6.0 FINAL.pdf
- **확장 계획**: `PROJECT_ROADMAP_V2_ADVANCED.md` (작성 예정)

### 기술 문서
- **FastAPI**: https://fastapi.tiangolo.com
- **OpenAI API**: https://platform.openai.com/docs
- **ChromaDB**: https://docs.trychroma.com
- **Streamlit**: https://docs.streamlit.io
- **Wikipedia-API**: https://pypi.org/project/Wikipedia-API/

### 학습 자료
- **RAG 개념**: https://www.pinecone.io/learn/retrieval-augmented-generation/
- **Map-Reduce**: https://en.wikipedia.org/wiki/MapReduce
- **Prompt Engineering**: https://www.promptingguide.ai/

---

## 16. 작성 정보

**문서명**: PROJECT_ROADMAP_V2_BASIC.md
**버전**: 1.0
**작성일**: 2025-10-18
**작성자**: FastCampus Project Team
**상태**: ✅ 최종 확정

**다음 단계**
1. ✅ v2.0 기본 계획 완료
2. ⏳ v2.0 고급 계획 작성
3. ⏳ 개발 시작 (Day 1)

---

**프로젝트 상태**: 🚀 **v2.0 기본 계획 완료**
**다음 목표**: v2.0 개발 시작
