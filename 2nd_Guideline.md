# 📋 SynapseSimple v2.0 - 순차적 개발 지침서 (개정판)

---

## 🎯 개요

**목적**: PROJECT_ROADMAP_V2_BASIC.md를 단계별 구현

**총 기간**: 10일 (80시간)

**원칙**:

- 계획서 참조 중심
- 핵심 지시만 제공
- VSCode Claude의 사고 유도
- 검증 위주

---

## 📅 Day 1: 프로젝트 설정 & 기반 구조 (8h)

### Step 1-1: 프로젝트 초기화 (1h)

**참조**: 계획서 13절 폴더 구조

**목적**: 프로젝트 뼈대 구축

**작업**:

- Git 저장소 초기화
- 계획서 13절 폴더 구조 그대로 생성
- .gitignore (Python 표준 + data/*)
- README.md 빈 파일

**검증**:

```bash
tree -L 2  # 폴더 구조 확인
git status  # Git 작동 확인
```

---

### Step 1-2: 환경 설정 (1.5h)

**참조**: 계획서 6.1절

**목적**: 개발 환경 준비

**작업**:

- requirements.txt 작성 (계획서 6.1절 그대로)
- .env.example 생성 (OPENAI_API_KEY 등)
- .env 복사 및 실제 키 입력
- 가상환경 생성 & 패키지 설치

**검증**:

```bash
pip list | grep openai  # 설치 확인
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY')[:5])"
```

---

### Step 1-3: config.py 작성 (1h)

**참조**: 계획서 부록 C (개발 환경 설정)

**목적**: 중앙 설정 관리

**핵심**:

- pydantic_settings.BaseSettings 사용
- .env 자동 로드
- 주요 설정: API 키, 경로, 모델명

**위치**: `backend/config.py`

**검증**:

```python
from backend.config import settings
print(settings.openai_api_key[:10])
print(settings.default_model)
```

---

### Step 1-4: logger.py 작성 (0.5h)

**참조**: Day 1 Step 1-5 (기존 계획서)

**목적**: 통합 로깅

**핵심**:

- setup_logger(name) 함수
- JSON 포맷 (pythonjsonlogger)
- stdout 출력

**위치**: `backend/utils/logger.py`

**검증**:

```python
from backend.utils.logger import setup_logger
logger = setup_logger('test')
logger.info('Test message')  # JSON 출력 확인
```

---

### Step 1-5: BaseAgent 구현 (3h) ⭐

**참조**: 계획서 3.3절, 4절, 부록 A

**목적**: 모든 에이전트의 추상 기반 클래스

**핵심 메서드**:

1. `__init__`: config, logger 초기화
2. `execute`: 추상 메서드 (필수 구현)
3. `validate_input`: task_type 필드 확인
4. `_start_timer` / `_calculate_time`: 성능 측정
5. `_count_tokens`: tiktoken 사용

**설계 원칙** (계획서 3.3절):

- 단일 책임
- 상태 무저장
- 표준 인터페이스

**위치**: `backend/agents/base_agent.py`

**검증**:

- Mock 에이전트 만들어 테스트
- execute() 호출 가능
- 타이머 작동 확인

---

### Step 1-6: BaseAgent 테스트 (1h)

**참조**: 계획서 부록 D

**목적**: BaseAgent 검증

**테스트 케이스**:

1. Mock 에이전트 생성
2. execute() 실행
3. validate_input() 성공/실패
4. _count_tokens() 정확성

**위치**: `tests/test_agents/test_base_agent.py`

**실행**:

```bash
pytest tests/test_agents/test_base_agent.py -v
```

**기대**: 모든 테스트 통과 ✅

---

### Step 1-7: Git 커밋

**작업**:

```bash
git add .
git commit -m "Day 1: Project setup and BaseAgent

- Folder structure
- Config and logger
- BaseAgent abstract class
- Unit tests
"
```

---

## 📅 Day 2: 서비스 레이어 (8h)

### Step 2-1: OpenAI Client (2h)

**참조**: 계획서 4절 (모든 에이전트가 사용)

**목적**: OpenAI API 통합 래퍼

**핵심**:

- openai.OpenAI 클라이언트 초기화
- chat_completion() 메서드
- tenacity 재시도 로직 (3회)
- 파라미터: model, messages, temperature, response_format

**위치**: `backend/services/openai_client.py`

**검증**:

```python
client = OpenAIClient()
response = await client.chat_completion(
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

---

### Step 2-2: EmbeddingService (1.5h)

**참조**: 계획서 4.1절 DocumentAgent

**목적**: 텍스트 → 벡터 변환

**핵심**:

- generate_embedding(text) → 단일
- generate_embeddings(texts) → 다중
- model: text-embedding-3-small

**위치**: `backend/services/embedding_service.py`

**검증**:

```python
service = EmbeddingService()
vector = await service.generate_embedding("테스트")
print(len(vector))  # 1536
```

---

### Step 2-3: TextProcessor (1.5h)

**참조**: 계획서 4.1절 DocumentAgent 청킹

**목적**: 텍스트 청킹

**핵심 메서드**:

- chunk_text(text, chunk_size=500, overlap=50)
- 문장 경계 고려 (마침표/개행)
- clean_text(text) - 공백 정리

**위치**: `backend/utils/text_processor.py`

**검증**:

```python
processor = TextProcessor()
chunks = processor.chunk_text("긴 텍스트..." * 100)
print(len(chunks))
print(len(chunks[0]))  # ~500자
```

---

### Step 2-4: OCRService (1h)

**참조**: 계획서 4.1절 DocumentAgent

**목적**: PDF 텍스트 추출

**핵심**:

- PyMuPDF (fitz) 사용
- extract_text(pdf_path) → str
- 페이지별 순회 후 결합

**위치**: `backend/services/ocr_service.py`

**검증**:

- 샘플 PDF로 테스트
- 텍스트 길이 확인

---

### Step 2-5: FileValidator (1h)

**참조**: 계획서 4.1절 DocumentAgent 검증

**목적**: 보안 파일 검증

**검증 항목**:

1. 파일 존재
2. 확장자 (.pdf만)
3. 크기 (50MB 이하)
4. 읽기 권한

**위치**: `backend/utils/file_validator.py`

**검증**:

- 유효 파일 → True
- 무효 파일 → ValueError

---

### Step 2-6: WikipediaService (1h)

**참조**: 계획서 4.9절 RecommendationAgent

**목적**: Wikipedia 검색

**핵심**:

- wikipedia-api 라이브러리
- search(query, max_results=3)
- 반환: title, url, summary

**위치**: `backend/services/wikipedia_service.py`

**검증**:

```python
service = WikipediaService()
results = service.search("토마토")
print(results[0]['title'])
```

---

### Step 2-7: Git 커밋

```bash
git commit -m "Day 2: Service layer

- OpenAI client
- Embedding service
- Text processor
- OCR service
- File validator
- Wikipedia service
"
```

---

## 📅 Day 3: 데이터베이스 (8h)

### Step 3-1: SQLite 스키마 (1h)

**참조**: 계획서 7.1절

**작업**:

- schema.sql 파일 생성
- 10개 테이블 정의 (계획서 그대로)
- 인덱스 3개

**위치**: `backend/db/schema.sql`

**검증**:

```bash
sqlite3 test.db < backend/db/schema.sql
sqlite3 test.db ".tables"  # 10개 테이블 확인
```

---

### Step 3-2: StateDB 클래스 (5h) ⭐

**참조**: 계획서 7절

**목적**: SQLite CRUD 래퍼

**핵심 메서드 그룹**:

1. **세션**: create_session, get_session
2. **요약**: save_document_summary, get_document_summary
3. **퀴즈**: save_quiz, get_quiz
4. **결과**: save_quiz_result, get_quiz_result
5. **프로필**: save_learner_profile, get_learner_profile
6. **계획**: save_learning_plan, get_learning_plan
7. **Q&A**: save_qa_history, get_qa_history
8. **대화**: save_conversation_summary, get_conversation_summary
9. **평가**: save_evaluation, get_evaluation
10. **추천**: save_recommendations, get_recommendations

**설계**:

- aiosqlite 사용 (비동기)
- JSON 필드는 json.dumps/loads
- _ensure_db()로 초기화

**위치**: `backend/db/state_db.py`

**힌트**:

- 계획서에 각 메서드 시그니처 있음
- 패턴 유사 → 템플릿화 가능

**검증**:

```python
db = StateDB()
await db.create_session("test-123", "test.pdf", "path")
session = await db.get_session("test-123")
print(session)
```

---

### Step 3-3: VectorDB 클래스 (1.5h)

**참조**: 계획서 4.1절 DocumentAgent, 4.5절 RAGAgent

**목적**: ChromaDB 래퍼

**핵심 메서드**:

1. add_documents(session_id, documents, embeddings)
2. search(session_id, query_embedding, top_k)
3. sample_chunks(session_id, n) - 랜덤 샘플링
4. delete_session(session_id)

**설계**:

- chromadb.PersistentClient
- 컬렉션명: f"session_{session_id}"

**위치**: `backend/db/vector_db.py`

**검증**:

```python
vdb = VectorDB()
vdb.add_documents("test", ["text1", "text2"], [[0.1]*1536, [0.2]*1536])
results = vdb.search("test", [0.15]*1536, top_k=2)
print(results)
```

---

### Step 3-4: SummaryCache 클래스 (0.5h)

**참조**: 계획서 4.2절 SummaryAgent 캐싱

**목적**: 요약 캐시 (파일 기반)

**핵심**:

- get(key) → Optional[dict]
- set(key, value, ttl=86400)
- 파일명: MD5(key).json
- TTL 체크

**위치**: `backend/utils/summary_cache.py`

**검증**:

```python
cache = SummaryCache()
cache.set("test", {"data": "value"})
result = cache.get("test")
print(result)
```

---

### Step 3-5: Git 커밋

```bash
git commit -m "Day 3: Database layer

- SQLite schema
- StateDB CRUD
- VectorDB wrapper
- Summary cache
"
```

---

## 📅 Day 4: DocumentAgent & SummaryAgent (8h)

### Step 4-1: DocumentAgent (4h) ⭐

**참조**: 계획서 4.1절

**목적**: PDF → 벡터 저장 파이프라인

**execute() 흐름**:

1. FileValidator.validate()
2. OCRService.extract_text()
3. TextProcessor.chunk_text()
4. EmbeddingService.generate_embeddings()
5. VectorDB.add_documents()

**의존성**:

- FileValidator
- OCRService
- TextProcessor
- EmbeddingService
- VectorDB

**위치**: `backend/agents/document_agent.py`

**검증**:

```python
agent = DocumentAgent(config)
result = await agent.execute({
    "task_type": "process_document",
    "file_path": "test.pdf",
    "session_id": "test-123"
})
print(result['status'])  # success
print(result['chunks_count'])
```

---

### Step 4-2: SummaryAgent (4h) ⭐

**참조**: 계획서 4.2절

**목적**: 문서 요약 생성

**execute() 흐름**:

1. 캐시 확인 (SummaryCache)
2. 토큰 수 계산
3. < 3000: _direct_summarize()
4. ≥ 3000: _map_reduce_summarize()
5. 품질 평가 _evaluate_quality()
6. 캐시 & DB 저장

**핵심 메서드**:

- _direct_summarize(): LLM 직접 호출
- _map_reduce_summarize(): 청크별 → 통합
- _evaluate_quality(): 점수 계산 (0-1)

**의존성**:

- OpenAIClient
- SummaryCache
- StateDB
- tiktoken

**위치**: `backend/agents/summary_agent.py`

**프롬프트**: `prompts/summary_prompts.py`에 분리

**검증**:

```python
agent = SummaryAgent(config)
result = await agent.execute({
    "task_type": "summarize_document",
    "session_id": "test-123",
    "summary_type": "balanced"
})
print(result['summary']['tldr'])
print(result['cache_hit'])
```

---

### Step 4-3: Git 커밋

```bash
git commit -m "Day 4: DocumentAgent and SummaryAgent

- Document processing pipeline
- Summary generation with caching
- Map-Reduce for long documents
"
```

---

## 📅 Day 5: Quiz & Grading Agents (8h)

### Step 5-1: QuizAgent (4h)

**참조**: 계획서 4.3절

**목적**: 객관식 5문항 생성

**execute() 흐름**:

1. StateDB에서 요약 조회 (key_concepts)
2. VectorDB 샘플링 (5개 청크)
3. LLM으로 퀴즈 생성
4. JSON 검증
5. StateDB 저장

**LLM 프롬프트**:

- 핵심 개념 기반
- 4지선다
- 난이도 분포 (쉬움2/보통2/어려움1)
- response_format: {"type": "json_object"}

**위치**: `backend/agents/quiz_agent.py`

**프롬프트**: `prompts/quiz_prompts.py`

**검증**:

```python
agent = QuizAgent(config)
result = await agent.execute({
    "task_type": "generate_quiz",
    "session_id": "test-123",
    "num_questions": 5
})
print(len(result['questions']))  # 5
```

---

### Step 5-2: GradingAgent (2h)

**참조**: 계획서 4.4절

**목적**: 객관식 자동 채점

**execute() 흐름**:

1. StateDB에서 퀴즈 조회
2. 사용자 답안과 비교 (인덱스)
3. 점수 계산 (0-100)
4. 결과 리스트 생성
5. StateDB 저장

**로직**: 간단한 인덱스 비교

**위치**: `backend/agents/grading_agent.py`

**검증**:

```python
agent = GradingAgent(config)
result = await agent.execute({
    "task_type": "grade_quiz",
    "quiz_id": "quiz-789",
    "answers": [1, 0, 2, 1, 3]
})
print(result['score'])  # 80
```

---

### Step 5-3: DiagnosisAgent (2h)

**참조**: 계획서 4.6절

**목적**: 학습자 레벨 판정

**execute() 흐름**:

1. StateDB에서 퀴즈 결과 조회
2. _determine_level(score) - 점수별 레벨
3. _analyze_concept_mastery() - 개념별 정답률
4. 강점/약점 파악
5. 프로필 저장

**레벨 기준**:

- 0-40: beginner
- 41-70: intermediate
- 71-100: advanced

**위치**: `backend/agents/diagnosis_agent.py`

**검증**:

```python
agent = DiagnosisAgent(config)
result = await agent.execute({
    "task_type": "diagnose_learner",
    "session_id": "test-123",
    "quiz_id": "quiz-789"
})
print(result['profile']['level'])  # intermediate
```

---

### Step 5-4: Git 커밋

```bash
git commit -m "Day 5: Quiz and diagnostic system

- QuizAgent: 5-question generation
- GradingAgent: auto-grading
- DiagnosisAgent: level assessment
"
```

---

## 📅 Day 6: RAG & Planning Agents (8h)

### Step 6-1: RAGAgent (4h) ⭐

**참조**: 계획서 4.5절

**목적**: 문서 기반 Q&A

**execute() 흐름**:

1. EmbeddingService로 질문 임베딩
2. VectorDB.search(top_k=5)
3. 유사도 필터링 (> 0.7)
4. _build_context() - 3000 토큰 이내
5. LLM 답변 생성
6. StateDB Q&A 기록

**답변 없음 처리**:

- filtered_results 비면 status: "no_answer"

**위치**: `backend/agents/rag_agent.py`

**검증**:

```python
agent = RAGAgent(config)
result = await agent.execute({
    "task_type": "answer_question",
    "session_id": "test-123",
    "question": "토마토 물주기?"
})
print(result['answer'])
print(result['sources'])
```

---

### Step 6-2: PlanningAgent (3h)

**참조**: 계획서 4.7절

**목적**: 맞춤형 학습 계획 생성

**execute() 흐름**:

1. StateDB에서 프로필 조회
2. StateDB에서 요약 조회
3. _get_template(level) - 레벨별 템플릿
4. LLM으로 맞춤 계획 생성
5. StateDB 저장

**템플릿**:

- beginner: 2-3주 / 2-3주 / 1-2주
- intermediate: 1-2주 / 2-3주 / 1-2주
- advanced: 1주 / 1-2주 / 2-3주

**위치**: `backend/agents/planning_agent.py`

**프롬프트**: `prompts/planning_prompts.py`

**검증**:

```python
agent = PlanningAgent(config)
result = await agent.execute({
    "task_type": "create_plan",
    "session_id": "test-123"
})
print(len(result['plan']['phases']))  # 3
```

---

### Step 6-3: Git 커밋

```bash
git commit -m "Day 6: RAG and planning

- RAGAgent: document Q&A
- PlanningAgent: personalized study plan
"
```

---

## 📅 Day 7: 평가 & 대화 Agents (8h)

### Step 7-1: ConversationAgent (3h)

**참조**: 계획서 4.10절

**목적**: 대화 요약

**execute() 흐름**:

1. StateDB에서 Q&A 기록 조회
2. LLM으로 대화 요약 (_summarize_conversation_llm)
3. _analyze_learning_patterns() - 주제/질문 유형
4. 종합 요약 생성
5. StateDB 저장

**LLM 추출**:

- key_learnings
- new_concepts
- review_points

**위치**: `backend/agents/conversation_agent.py`

**검증**:

```python
agent = ConversationAgent(config)
result = await agent.execute({
    "task_type": "summarize_conversation",
    "session_id": "test-123"
})
print(result['conversation_summary']['key_learnings'])
```

---

### Step 7-2: EvaluationAgent (3h)

**참조**: 계획서 4.8절

**목적**: 세션 종합 평가

**execute() 흐름**:

1. StateDB에서 프로필, Q&A 기록 조회
2. _analyze_quiz_performance()
3. _analyze_qa_activity()
4. _estimate_time_spent()
5. LLM 피드백 생성
6. _recommend_next_steps()
7. StateDB 저장

**위치**: `backend/agents/evaluation_agent.py`

**검증**:

```python
agent = EvaluationAgent(config)
result = await agent.execute({
    "task_type": "evaluate_session",
    "session_id": "test-123"
})
print(result['evaluation']['feedback'])
```

---

### Step 7-3: RecommendationAgent (2h)

**참조**: 계획서 4.9절

**목적**: 추가 자료 추천

**execute() 흐름**:

1. 프로필 조회 (약점 파악)
2. WikipediaService.search()
3. 결과 포맷팅
4. StateDB 저장

**위치**: `backend/agents/recommendation_agent.py`

**검증**:

```python
agent = RecommendationAgent(config)
result = await agent.execute({
    "task_type": "recommend_resources",
    "topic": "토마토 재배"
})
print(len(result['recommendations']))  # 3
```

---

### Step 7-4: Git 커밋

```bash
git commit -m "Day 7: Evaluation and conversation

- ConversationAgent: dialogue summary
- EvaluationAgent: session assessment
- RecommendationAgent: resource suggestions
"
```

---

## 📅 Day 8: OrchestratorAgent (8h) ⭐

### Step 8-1: OrchestratorAgent 구현 (6h)

**참조**: 계획서 4.11절, 3.2절

**목적**: 에이전트 조율

**핵심 구조**:

```python
class OrchestratorAgent:
    def __init__(self):
        self.agents = {
            'document': DocumentAgent(),
            'summary': SummaryAgent(),
            # ... 10개 전체
        }
        
        self.workflows = {
            'onboard_document': self._workflow_onboard_document,
            'learning_diagnosis': self._workflow_learning_diagnosis,
            'qa_session': self._workflow_qa_session,
            'session_evaluation': self._workflow_session_evaluation
        }
```

**4개 워크플로우 구현**:

1. **onboard_document**:
    
    - DocumentAgent → SummaryAgent
2. **learning_diagnosis**:
    
    - QuizAgent → GradingAgent → DiagnosisAgent → PlanningAgent
3. **qa_session**:
    
    - RAGAgent
4. **session_evaluation**:
    
    - ConversationAgent → EvaluationAgent → RecommendationAgent

**위치**: `backend/agents/orchestrator_agent.py`

**검증**:

```python
orchestrator = OrchestratorAgent(config)
result = await orchestrator.execute({
    "workflow": "onboard_document",
    "params": {"file_path": "test.pdf", "session_id": "test"}
})
print(result['agents_used'])  # ['DocumentAgent', 'SummaryAgent']
```

---

### Step 8-2: 통합 테스트 (2h)

**목적**: 전체 워크플로우 검증

**테스트 시나리오**:

1. 문서 업로드 → 요약
2. 퀴즈 생성 → 채점 → 진단 → 계획
3. Q&A 5회
4. 대화 요약 → 평가 → 추천

**위치**: `tests/test_integration/test_workflows.py`

**검증**:

- 모든 워크플로우 성공
- 10개 에이전트 작동
- DB 저장 확인

---

### Step 8-3: Git 커밋

```bash
git commit -m "Day 8: Orchestrator and integration

- OrchestratorAgent: workflow coordination
- 4 main workflows implemented
- Integration tests
"
```

---

## 📅 Day 9: API & Frontend (8h)

### Step 9-1: FastAPI 엔드포인트 (4h)

**참조**: 계획서 8.1절, 8.2절

**목적**: REST API 구축

**10개 엔드포인트**:

```python
# main.py
app = FastAPI()

# 파일 업로드
@app.post("/api/upload")
async def upload_document(file: UploadFile):
    # OrchestratorAgent.workflow_onboard_document

# 요약 조회
@app.get("/api/summary/document/{session_id}")

# 대화 요약
@app.post("/api/summary/conversation")

# 퀴즈 생성
@app.post("/api/diagnosis/{session_id}")

# 퀴즈 제출
@app.post("/api/diagnosis/submit")

# Q&A
@app.post("/api/ask")

# 학습 계획
@app.get("/api/plan/{session_id}")

# 세션 평가
@app.post("/api/evaluation/{session_id}")

# 자료 추천
@app.get("/api/recommendations/{session_id}")

# 헬스체크
@app.get("/api/health")
```

**Pydantic 모델**: `backend/api/models.py`

**위치**: `backend/main.py`, `backend/api/routes/`

**검증**:

```bash
uvicorn backend.main:app --reload
curl http://localhost:8000/api/health
```

---

### Step 9-2: Streamlit Frontend (4h)

**참조**: 계획서 5절 UI 예시, 13절 구조

**6개 페이지**:

1. **Home (1_Home.py)**: 업로드 + 요약 표시
2. **Diagnosis (2_Diagnosis.py)**: 퀴즈 + 결과
3. **QA (3_QA.py)**: 채팅 인터페이스
4. **Dashboard (4_Dashboard.py)**: 프로필 + 통계
5. **Plan (5_Plan.py)**: 학습 계획
6. **Resources (6_Resources.py)**: 추가 자료

**API Client**: `frontend/utils/api_client.py`

- requests 라이브러리
- 모든 API 호출 래핑

**위치**: `frontend/`

**검증**:

```bash
streamlit run frontend/app.py
# 브라우저에서 전체 플로우 테스트
```

---

### Step 9-3: Git 커밋

```bash
git commit -m "Day 9: API and Frontend

- FastAPI: 10 endpoints
- Streamlit: 6 pages
- Complete UI flow
"
```

---

## 📅 Day 10: 테스트 & 문서화 (8h)

### Step 10-1: E2E 테스트 (3h)

**목적**: 전체 시나리오 검증

**시나리오**: 계획서 14절 참조

1. PDF 업로드 → 요약 확인
2. 진단 퀴즈 → 결과 확인
3. Q&A 10회
4. 대화 요약
5. 학습 계획 조회
6. 추가 자료 조회

**위치**: `tests/test_e2e/test_complete_flow.py`

**검증**: 모든 단계 성공 ✅

---

### Step 10-2: 성능 테스트 (2h)

**목적**: KPI 검증 (계획서 10절)

**측정 항목**:

- 문서 처리: < 10초
- 요약 생성: < 10초 (캐시 히트: < 1초)
- Q&A 응답: < 5초
- 퀴즈 생성: < 5초

**도구**: pytest-benchmark

**검증**: 모든 KPI 달성

---

### Step 10-3: 문서화 (3h)

**작성 문서**:

1. **README.md**:
    
    - 프로젝트 개요
    - 10개 에이전트 소개
    - 설치 방법
    - 실행 방법
    - 시연 영상/GIF
2. **ARCHITECTURE.md** (docs/):
    
    - 계획서 3절 다이어그램
    - 에이전트 관계도
    - 데이터 흐름
3. **API.md** (docs/):
    
    - 10개 엔드포인트 상세
    - Request/Response 예시
4. **AGENTS.md** (docs/):
    
    - 10개 에이전트 각각 설명
    - 입력/출력 명세

**검증**: 문서 완성도 확인

---

### Step 10-4: 최종 커밋 & 태그

```bash
git add .
git commit -m "Day 10: Testing and documentation

- E2E tests
- Performance benchmarks
- Complete documentation
"

git tag -a v2.0-basic -m "SynapseSimple v2.0 Basic - 10 Agent System"
git push origin main --tags
```

---

## ✅ 완료 체크리스트

### 기능 (학원 요구사항)

- [ ] 문서 요약 (SummaryAgent)
- [ ] Q&A (RAGAgent)
- [ ] 문제 생성 (QuizAgent)
- [ ] 자료 추천 (RecommendationAgent)

### 에이전트 시스템

- [ ] BaseAgent 추상 클래스
- [ ] 10개 에이전트 구현
- [ ] OrchestratorAgent 조율
- [ ] 4개 워크플로우

### 데이터베이스

- [ ] SQLite 10개 테이블
- [ ] StateDB CRUD
- [ ] VectorDB (ChromaDB)

### API & UI

- [ ] FastAPI 10개 엔드포인트
- [ ] Streamlit 6개 페이지
- [ ] 전체 플로우 작동

### 테스트 & 문서

- [ ] 단위 테스트 (80%+ 커버리지)
- [ ] E2E 테스트
- [ ] 성능 테스트 (KPI 달성)
- [ ] 문서 4개 완성

---

## 📞 도움 요청

각 Step에서 막히면:

1. **계획서 재확인**: 해당 섹션 다시 읽기
2. **로그 확인**: logger 출력 분석
3. **단위 테스트**: 작은 단위로 검증
4. **Issue 등록**: GitHub Issues에 질문

---

## 🎯 최종 목표

**v2.0 기본 완성!**

- ✅ 10개 전문 에이전트 시스템
- ✅ 학원 요구사항 100% 충족
- ✅ 엔터프라이즈급 아키텍처
- ✅ 포트폴리오 차별화

**다음 단계**: v2.0 고급 (AI 채점, 다양한 퀴즈)

---

**이제 Day 1부터 시작하세요!** 🚀