# 📚 SynapseSimple v2.0 기본 - 10개 에이전트 시스템 계획서

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [v1.0 vs v2.0 비교](#2-v10-vs-v20-비교)
3. [10개 에이전트 시스템 아키텍처](#3-10개-에이전트-시스템-아키텍처)
4. [에이전트 상세 명세](#4-에이전트-상세-명세)
5. [핵심 기능 명세](#5-핵심-기능-명세)
6. [기술 스택](#6-기술-스택)
7. [데이터 모델](#7-데이터-모델)
8. [API 설계](#8-api-설계)
9. [개발 로드맵](#9-개발-로드맵)
10. [성공 지표](#10-성공-지표)
11. [비용 예산](#11-비용-예산)
12. [확장 계획](#12-확장-계획)

---

## 1. 프로젝트 개요

### 1.1 과제 배경 및 목적

**배경**: 
ChatGPT, Claude와 같은 대규모 언어모델(LLM)의 등장은 교육·업무·연구 현장에서 문서를 빠르게 이해하고 활용할 수 있는 가능성을 열었습니다. 그러나 단순 대화형 사용에서 벗어나 특정 목적(학습 지원)에 맞는 챗봇 서비스 설계 경험은 학생들에게 필요합니다.

**목적**:
- 교육생들이 LLM API를 직접 연동하고 프롬프트를 설계해봄으로써, 실제 서비스가 동작하는 과정을 경험
- 서비스 기획 → 개발 → 시연의 전 과정을 경험하며 포트폴리오로 활용
- 팀 단위 협업과 발표를 통해 문제 해결 능력 강화

**해결하고자 하는 문제**:
1. 방대한 문서를 짧은 시간에 이해하기 어렵다
2. 학습자 수준에 맞는 문제/과제를 자동으로 만들기 어렵다
3. 개별 학습자에게 적합한 자료 추천이 부족하다

**기대 효과**:
- LLM API를 활용한 요약, Q&A, 문제 생성, 자료 추천 챗봇을 직접 만들어보며 실무형 역량 습득
- **10개 전문 에이전트 시스템**을 통한 고급 아키텍처 경험
- 실제 서비스 수준의 완성도 있는 프로젝트

---

### 1.2 v1.0 완료 현황

**Phase 1-6 완료**:
- ✅ PDF 업로드 및 저장
- ✅ 텍스트 추출 (PyMuPDF)
- ✅ 청킹 (500자, 50자 오버랩)
- ✅ 임베딩 생성 (OpenAI text-embedding-3-small)
- ✅ ChromaDB 저장 (Persistent)
- ✅ Streamlit 조회

**기술 스택**:
- Backend: FastAPI 0.104.1
- Frontend: Streamlit 1.31.0
- DB: ChromaDB 0.4.22
- AI: OpenAI API
- PDF: PyMuPDF 1.26.5

**성과**:
- 처리 시간: ~10초
- 텍스트 추출: 95%+ 성공률
- Git 버전 관리 완료
- GitHub 배포 준비

---

### 1.3 v2.0 목표

**학원 필수 요구사항 충족 + 전문 에이전트 시스템**

**핵심 차별화**:
- 🎯 **10개 전문 에이전트**: 각 기능별 특화된 AI 에이전트
- 🤖 **오케스트레이션**: 에이전트 간 협업 및 조율
- 📊 **지능형 학습 지원**: 진단 → 계획 → 실행 → 평가 전 주기
- 🔄 **확장 가능한 아키텍처**: 새로운 에이전트 추가 용이

---

## 2. v1.0 vs v2.0 비교

| 구분 | v1.0 (완료) | v2.0 기본 (10개 에이전트) |
|------|-------------|---------------------------|
| **아키텍처** | 단순 파이프라인 | 멀티 에이전트 시스템 ⭐ |
| **에이전트** | 0개 | 10개 전문 에이전트 ⭐ |
| **PDF 처리** | ✅ PyMuPDF | ✅ (DocumentAgent) |
| **벡터 저장** | ✅ | ✅ (DocumentAgent) |
| **문서 요약** | ❌ | ✅ SummaryAgent ⭐ |
| **Q&A** | ❌ | ✅ RAGAgent ⭐ |
| **문제 생성** | ❌ | ✅ QuizAgent ⭐ |
| **채점** | ❌ | ✅ GradingAgent ⭐ |
| **학습 진단** | ❌ | ✅ DiagnosisAgent ⭐ |
| **학습 계획** | ❌ | ✅ PlanningAgent ⭐ |
| **자료 추천** | ❌ | ✅ RecommendationAgent ⭐ |
| **평가** | ❌ | ✅ EvaluationAgent ⭐ |
| **조율** | ❌ | ✅ OrchestratorAgent ⭐ |
| **대화 요약** | ❌ | ✅ ConversationAgent ⭐ |

---

## 3. 10개 에이전트 시스템 아키텍처

### 3.1 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Streamlit)                   │
│  - 파일 업로드  - 요약 보기  - Q&A  - 퀴즈  - 대시보드  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP REST API
┌────────────────────┴────────────────────────────────────┐
│              Backend (FastAPI) - API Layer               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                 OrchestratorAgent                        │
│          (에이전트 간 조율 및 워크플로우 관리)           │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───┘
   │      │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Document│Summary│  Quiz │Grading│  RAG  │Diagnosis│
│ Agent │ Agent │ Agent │ Agent │ Agent │ Agent  │
└───┬───┘ └───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘ └───┬───┘
    │         │        │        │        │        │
┌───▼──┐ ┌───▼──┐ ┌───▼──┐ ┌───▼──────────────▼─────┐
│Planning│Evaluation│Recommendation│Conversation      │
│ Agent │  Agent   │    Agent     │    Agent         │
└───┬───┘ └───┬───┘ └──────┬──────┘ └────────┬──────┘
    │         │             │                 │
    └─────────┴─────────────┴─────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                  Storage Layer                           │
│  - ChromaDB (벡터)  - SQLite (상태)  - Cache (요약)     │
└─────────────────────────────────────────────────────────┘
```

---

### 3.2 에이전트 간 협업 흐름

**시나리오: 새 문서 업로드**

```
1. User → API: PDF 업로드
2. OrchestratorAgent → DocumentAgent: 문서 처리 요청
3. DocumentAgent: 
   - 텍스트 추출 (OCR)
   - 청킹 (500자)
   - 임베딩 생성
   - ChromaDB 저장
4. OrchestratorAgent → SummaryAgent: 요약 생성 요청
5. SummaryAgent:
   - 캐시 확인
   - Map-Reduce 요약 (필요시)
   - 품질 평가
   - SQLite 저장
6. OrchestratorAgent → User: 완료 응답 (요약 포함)
```

**시나리오: 학습 진단 퀴즈**

```
1. User → API: 진단 퀴즈 생성 요청
2. OrchestratorAgent → DiagnosisAgent: 사전 진단
3. DiagnosisAgent → SummaryAgent: 문서 요약 조회
4. DiagnosisAgent → QuizAgent: 퀴즈 생성 요청
5. QuizAgent:
   - 문서 요약의 key_concepts 활용
   - ChromaDB 샘플링
   - LLM 5문항 생성 (객관식)
   - SQLite 저장
6. User: 퀴즈 풀이
7. OrchestratorAgent → GradingAgent: 채점 요청
8. GradingAgent:
   - 자동 채점 (객관식)
   - 점수 계산
   - SQLite 저장
9. OrchestratorAgent → DiagnosisAgent: 레벨 판정
10. OrchestratorAgent → PlanningAgent: 학습 계획 요청
11. PlanningAgent:
    - 진단 결과 기반
    - 요약 정보 활용
    - 맞춤 계획 생성
12. OrchestratorAgent → User: 종합 결과
```

**시나리오: Q&A 세션**

```
1. User → API: 질문 입력 (5-10회)
2. OrchestratorAgent → RAGAgent: 답변 요청
3. RAGAgent:
   - 질문 임베딩
   - ChromaDB 검색
   - LLM 답변 생성
   - ConversationAgent에 기록
4. (반복)
5. User: "지금까지 요약" 버튼
6. OrchestratorAgent → ConversationAgent: 대화 요약
7. ConversationAgent:
   - Q&A 기록 조회
   - 학습 패턴 분석
   - 요약 생성
8. OrchestratorAgent → User: 대화 요약 표시
```

---

### 3.3 에이전트 독립성과 재사용성

**설계 원칙**:
1. **단일 책임**: 각 에이전트는 하나의 핵심 기능만 담당
2. **느슨한 결합**: 에이전트 간 직접 호출 금지 (OrchestratorAgent 경유)
3. **표준 인터페이스**: 모든 에이전트는 동일한 BaseAgent 상속
4. **상태 무저장**: 에이전트는 상태를 가지지 않음 (DB에 저장)
5. **확장 가능**: 새 에이전트 추가 시 기존 코드 수정 최소화

```python
class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def execute(self, task: dict) -> dict:
        """에이전트 실행 (추상 메서드)"""
        pass
    
    def validate_input(self, task: dict) -> bool:
        """입력 검증"""
        pass
    
    def log_execution(self, task: dict, result: dict):
        """실행 로깅"""
        pass
```

---

## 4. 에이전트 상세 명세

### 4.1 DocumentAgent (문서 처리 에이전트)

**책임**: PDF 문서의 물리적 처리

**주요 기능**:
1. 파일 검증 (보안)
2. OCR 텍스트 추출 (PyMuPDF)
3. 텍스트 청킹 (500자, 50자 오버랩)
4. 임베딩 생성 (OpenAI)
5. ChromaDB 저장

**입력**:
```python
{
  "task_type": "process_document",
  "file_path": "data/uploads/document.pdf",
  "session_id": "abc-123"
}
```

**출력**:
```python
{
  "status": "success",
  "session_id": "abc-123",
  "text_length": 2500,
  "chunks_count": 6,
  "embeddings_count": 6,
  "processing_time": 8.5
}
```

**구현**:
```python
class DocumentAgent(BaseAgent):
    """문서 처리 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.file_validator = FileValidator()
        self.ocr_service = OCRService()
        self.text_processor = TextProcessor()
        self.embedding_service = EmbeddingService()
        self.vector_db = VectorDB()
    
    async def execute(self, task: dict) -> dict:
        """문서 처리 실행"""
        
        self.logger.info(f"📄 Starting document processing: {task['file_path']}")
        
        # 1. 파일 검증
        self.file_validator.validate(task['file_path'])
        
        # 2. 텍스트 추출
        text = self.ocr_service.extract_text(task['file_path'])
        self.logger.info(f"✅ Extracted {len(text)} characters")
        
        # 3. 청킹
        chunks = self.text_processor.chunk_text(text)
        self.logger.info(f"✅ Created {len(chunks)} chunks")
        
        # 4. 임베딩
        embeddings = await self.embedding_service.generate_embeddings(chunks)
        self.logger.info(f"✅ Generated {len(embeddings)} embeddings")
        
        # 5. 벡터 저장
        self.vector_db.add_documents(
            session_id=task['session_id'],
            documents=chunks,
            embeddings=embeddings
        )
        self.logger.info(f"✅ Saved to ChromaDB")
        
        return {
            "status": "success",
            "session_id": task['session_id'],
            "text_length": len(text),
            "text_preview": text[:200],
            "chunks_count": len(chunks),
            "embeddings_count": len(embeddings),
            "processing_time": self._calculate_time()
        }
```

**의존성**:
- FileValidator (보안)
- OCRService (PyMuPDF)
- TextProcessor (청킹)
- EmbeddingService (OpenAI)
- VectorDB (ChromaDB)

---

### 4.2 SummaryAgent (요약 에이전트) ⭐

**책임**: 문서 및 대화 요약 생성

**주요 기능**:
1. 문서 즉시 요약 (Map-Reduce)
2. 캐싱 시스템 (90% 비용 절감)
3. 품질 평가 (0-1 점수)
4. 3가지 요약 유형 (짧게/균형/상세)

**입력**:
```python
{
  "task_type": "summarize_document",
  "session_id": "abc-123",
  "summary_type": "balanced"  # brief/balanced/detailed
}
```

**출력**:
```python
{
  "status": "success",
  "summary": {
    "tldr": ["3줄 요약1", "3줄 요약2", "3줄 요약3"],
    "main_topic": "토마토 재배 가이드",
    "key_concepts": ["파종", "물주기", "병충해", "수확", "관리"],
    "difficulty_level": "intermediate",
    "estimated_time_minutes": 120,
    "quality_score": 0.85
  },
  "cache_hit": false,
  "processing_time": 5.2
}
```

**구현**:
```python
class SummaryAgent(BaseAgent):
    """요약 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.cache = SummaryCache()
        self.state_db = StateDB()
        self.llm = OpenAIClient()
    
    async def execute(self, task: dict) -> dict:
        """요약 생성 실행"""
        
        session_id = task['session_id']
        summary_type = task.get('summary_type', 'balanced')
        
        self.logger.info(f"📝 Summarizing document: {session_id}")
        
        # 1. 캐시 확인
        cache_key = self._generate_cache_key(session_id, summary_type)
        cached = self.cache.get(cache_key)
        
        if cached:
            self.logger.info("✅ Cache hit!")
            return {
                "status": "success",
                "summary": cached,
                "cache_hit": True,
                "processing_time": 0.1
            }
        
        # 2. 문서 텍스트 가져오기
        text = self._get_document_text(session_id)
        
        # 3. 토큰 수 계산
        token_count = self._count_tokens(text)
        self.logger.info(f"📊 Token count: {token_count}")
        
        # 4. 요약 전략 선택
        if token_count < 3000:
            # 직접 요약
            summary = await self._direct_summarize(text, summary_type)
        else:
            # Map-Reduce
            summary = await self._map_reduce_summarize(text, summary_type)
        
        # 5. 품질 평가
        quality_score = self._evaluate_quality(summary)
        summary['quality_score'] = quality_score
        
        self.logger.info(f"✅ Summary quality: {quality_score:.2f}")
        
        # 6. 캐시 저장
        self.cache.set(cache_key, summary, ttl=86400)  # 24시간
        
        # 7. DB 저장
        self.state_db.save_document_summary(session_id, summary)
        
        return {
            "status": "success",
            "summary": summary,
            "cache_hit": False,
            "processing_time": self._calculate_time()
        }
    
    async def _direct_summarize(self, text: str, summary_type: str) -> dict:
        """직접 요약 (짧은 문서)"""
        
        prompt = self._get_prompt(summary_type)
        
        response = await self.llm.chat_completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"다음 문서를 요약하세요:\n\n{text}"}
            ],
            temperature=0.3
        )
        
        return self._parse_summary(response)
    
    async def _map_reduce_summarize(self, text: str, summary_type: str) -> dict:
        """Map-Reduce 요약 (긴 문서)"""
        
        from concurrent.futures import ThreadPoolExecutor
        
        # Map: 청크별 요약
        chunks = self._split_for_map_reduce(text, chunk_size=2500, overlap=200)
        
        self.logger.info(f"🗺️ Map phase: {len(chunks)} chunks")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            chunk_summaries = list(executor.map(
                lambda c: self._summarize_chunk(c),
                chunks
            ))
        
        # Reduce: 통합 요약
        self.logger.info("🔄 Reduce phase")
        
        combined_text = "\n\n".join(chunk_summaries)
        final_summary = await self._direct_summarize(combined_text, summary_type)
        
        return final_summary
    
    def _evaluate_quality(self, summary: dict) -> float:
        """품질 평가 (0-1)"""
        
        score = 0.0
        
        # TL;DR 3개?
        if len(summary.get('tldr', [])) == 3:
            score += 0.25
        
        # key_concepts 3개+?
        if len(summary.get('key_concepts', [])) >= 3:
            score += 0.25
        
        # main_topic 존재?
        if summary.get('main_topic'):
            score += 0.25
        
        # difficulty_level 설정?
        if summary.get('difficulty_level') in ['beginner', 'intermediate', 'advanced']:
            score += 0.25
        
        return score
```

**의존성**:
- SummaryCache (캐싱)
- StateDB (저장)
- OpenAIClient (LLM)
- tiktoken (토큰 계산)

---

### 4.3 QuizAgent (퀴즈 생성 에이전트)

**책임**: 학습 평가 문제 생성

**주요 기능**:
1. 객관식 문제 생성 (4지선다, 5문항)
2. 문서 요약 기반 (key_concepts 활용)
3. 난이도 자동 조정
4. JSON 검증 및 저장

**입력**:
```python
{
  "task_type": "generate_quiz",
  "session_id": "abc-123",
  "num_questions": 5
}
```

**출력**:
```python
{
  "status": "success",
  "quiz_id": "quiz-789",
  "questions": [
    {
      "id": 1,
      "type": "multiple_choice",
      "question": "토마토 씨앗 파종 적기는?",
      "options": ["3월", "4월", "5월", "6월"],
      "correct_answer": 1,
      "explanation": "4월이 최적기입니다...",
      "difficulty": "easy",
      "concept": "파종"
    },
    // ... 4개 더
  ],
  "total_score": 100,
  "processing_time": 3.5
}
```

**구현**:
```python
class QuizAgent(BaseAgent):
    """퀴즈 생성 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.state_db = StateDB()
        self.vector_db = VectorDB()
        self.llm = OpenAIClient()
    
    async def execute(self, task: dict) -> dict:
        """퀴즈 생성 실행"""
        
        session_id = task['session_id']
        num_questions = task.get('num_questions', 5)
        
        self.logger.info(f"📝 Generating {num_questions} questions")
        
        # 1. 문서 요약 조회 (key_concepts 활용)
        summary = self.state_db.get_document_summary(session_id)
        
        if not summary:
            raise ValueError("Summary not found. Run SummaryAgent first.")
        
        key_concepts = summary.get('key_concepts', [])
        self.logger.info(f"🎯 Focus concepts: {key_concepts}")
        
        # 2. 대표 청크 샘플링
        sample_chunks = self.vector_db.sample_chunks(
            session_id=session_id,
            n=5
        )
        
        # 3. LLM으로 퀴즈 생성
        quiz_data = await self._generate_quiz_llm(
            key_concepts=key_concepts,
            sample_chunks=sample_chunks,
            num_questions=num_questions
        )
        
        # 4. JSON 검증
        validated_quiz = self._validate_quiz(quiz_data)
        
        # 5. DB 저장
        quiz_id = str(uuid.uuid4())
        self.state_db.save_quiz(
            quiz_id=quiz_id,
            session_id=session_id,
            quiz=validated_quiz
        )
        
        self.logger.info(f"✅ Quiz generated: {quiz_id}")
        
        return {
            "status": "success",
            "quiz_id": quiz_id,
            "questions": validated_quiz['questions'],
            "total_score": 100,
            "processing_time": self._calculate_time()
        }
    
    async def _generate_quiz_llm(
        self,
        key_concepts: List[str],
        sample_chunks: List[str],
        num_questions: int
    ) -> dict:
        """LLM으로 퀴즈 생성"""
        
        prompt = f"""
        당신은 농작물 재배 교육 전문가입니다.
        학습자의 이해도를 평가하는 객관식 퀴즈를 생성하세요.
        
        핵심 개념: {', '.join(key_concepts)}
        
        학습 자료 샘플:
        {chr(10).join(sample_chunks[:3])}
        
        요구사항:
        - 총 {num_questions}문항
        - 4지선다 객관식
        - 핵심 개념을 골고루 다룰 것
        - 난이도: 쉬움(2) / 보통(2) / 어려움(1)
        - 각 문제에 해설 포함
        
        JSON 형식으로 출력:
        {{
          "questions": [
            {{
              "question": "질문 내용",
              "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
              "correct_answer": 1,  // 0-3 인덱스
              "explanation": "해설",
              "difficulty": "easy",  // easy/medium/hard
              "concept": "파종"
            }}
          ]
        }}
        """
        
        response = await self.llm.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _validate_quiz(self, quiz_data: dict) -> dict:
        """퀴즈 검증"""
        
        questions = quiz_data.get('questions', [])
        
        for q in questions:
            # 필수 필드 확인
            assert 'question' in q
            assert 'options' in q and len(q['options']) == 4
            assert 'correct_answer' in q and 0 <= q['correct_answer'] < 4
            assert 'explanation' in q
            
            # ID 추가
            if 'id' not in q:
                q['id'] = questions.index(q) + 1
        
        return quiz_data
```

**의존성**:
- StateDB (요약 조회, 퀴즈 저장)
- VectorDB (샘플링)
- OpenAIClient (LLM)

---

### 4.4 GradingAgent (채점 에이전트)

**책임**: 퀴즈 답안 채점

**주요 기능**:
1. 객관식 자동 채점
2. 점수 계산 (0-100)
3. 정답/오답 분석
4. 결과 저장

**입력**:
```python
{
  "task_type": "grade_quiz",
  "quiz_id": "quiz-789",
  "answers": [1, 0, 2, 1, 3]  # 사용자 답안
}
```

**출력**:
```python
{
  "status": "success",
  "quiz_id": "quiz-789",
  "score": 80,
  "total_score": 100,
  "percentage": 80.0,
  "correct_count": 4,
  "wrong_count": 1,
  "results": [
    {
      "question_id": 1,
      "user_answer": 1,
      "correct_answer": 1,
      "is_correct": true,
      "explanation": "..."
    },
    // ... 4개 더
  ],
  "processing_time": 0.5
}
```

**구현**:
```python
class GradingAgent(BaseAgent):
    """채점 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.state_db = StateDB()
    
    async def execute(self, task: dict) -> dict:
        """채점 실행"""
        
        quiz_id = task['quiz_id']
        user_answers = task['answers']
        
        self.logger.info(f"📊 Grading quiz: {quiz_id}")
        
        # 1. 퀴즈 조회
        quiz = self.state_db.get_quiz(quiz_id)
        
        if not quiz:
            raise ValueError(f"Quiz not found: {quiz_id}")
        
        questions = quiz['questions']
        
        # 2. 채점
        results = []
        correct_count = 0
        
        for idx, question in enumerate(questions):
            user_answer = user_answers[idx]
            correct_answer = question['correct_answer']
            
            is_correct = (user_answer == correct_answer)
            
            if is_correct:
                correct_count += 1
            
            results.append({
                "question_id": question['id'],
                "question": question['question'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question['explanation'],
                "concept": question.get('concept', '')
            })
        
        # 3. 점수 계산
        total_questions = len(questions)
        score = int((correct_count / total_questions) * 100)
        percentage = (correct_count / total_questions) * 100
        
        self.logger.info(f"✅ Score: {score}/100 ({correct_count}/{total_questions})")
        
        # 4. 결과 저장
        self.state_db.save_quiz_result(
            quiz_id=quiz_id,
            score=score,
            results=results
        )
        
        return {
            "status": "success",
            "quiz_id": quiz_id,
            "score": score,
            "total_score": 100,
            "percentage": percentage,
            "correct_count": correct_count,
            "wrong_count": total_questions - correct_count,
            "results": results,
            "processing_time": self._calculate_time()
        }
```

**의존성**:
- StateDB (퀴즈 조회, 결과 저장)

---

### 4.5 RAGAgent (질문-답변 에이전트)

**책임**: 문서 기반 질문 답변

**주요 기능**:
1. 질문 임베딩 생성
2. ChromaDB 유사도 검색 (Top-5)
3. 컨텍스트 구성
4. LLM 답변 생성
5. Q&A 기록 저장

**입력**:
```python
{
  "task_type": "answer_question",
  "session_id": "abc-123",
  "question": "토마토 물주기 주기는?"
}
```

**출력**:
```python
{
  "status": "success",
  "question": "토마토 물주기 주기는?",
  "answer": "토마토는 하루에 1-2번 물을 주는 것이 적절합니다...",
  "sources": [
    {
      "chunk_id": 3,
      "text": "물주기는 토양 상태를 확인하여...",
      "similarity": 0.85
    },
    {
      "chunk_id": 7,
      "text": "과습을 피하고...",
      "similarity": 0.78
    }
  ],
  "processing_time": 2.3
}
```

**구현**:
```python
class RAGAgent(BaseAgent):
    """RAG 기반 Q&A 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.embedding_service = EmbeddingService()
        self.vector_db = VectorDB()
        self.llm = OpenAIClient()
        self.state_db = StateDB()
    
    async def execute(self, task: dict) -> dict:
        """질문 답변 실행"""
        
        session_id = task['session_id']
        question = task['question']
        
        self.logger.info(f"❓ Question: {question}")
        
        # 1. 질문 임베딩
        question_embedding = await self.embedding_service.generate_embedding(question)
        
        # 2. 유사도 검색
        search_results = self.vector_db.search(
            session_id=session_id,
            query_embedding=question_embedding,
            top_k=5
        )
        
        self.logger.info(f"🔍 Found {len(search_results)} relevant chunks")
        
        # 3. 유사도 필터링 (> 0.7)
        filtered_results = [
            r for r in search_results
            if r['similarity'] > 0.7
        ]
        
        if not filtered_results:
            self.logger.warning("⚠️ No relevant chunks found")
            return {
                "status": "no_answer",
                "question": question,
                "answer": None,
                "message": "관련 정보를 찾을 수 없습니다."
            }
        
        # 4. 컨텍스트 구성
        context = self._build_context(filtered_results, max_tokens=3000)
        
        # 5. LLM 답변 생성
        answer = await self._generate_answer(question, context)
        
        self.logger.info(f"✅ Answer generated")
        
        # 6. Q&A 기록 저장 (ConversationAgent용)
        self.state_db.save_qa_history(
            session_id=session_id,
            question=question,
            answer=answer,
            sources=[{
                "chunk_id": r['chunk_id'],
                "similarity": r['similarity']
            } for r in filtered_results]
        )
        
        return {
            "status": "success",
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "chunk_id": r['chunk_id'],
                    "text": r['text'][:200] + "...",
                    "similarity": round(r['similarity'], 2)
                }
                for r in filtered_results[:3]
            ],
            "processing_time": self._calculate_time()
        }
    
    def _build_context(self, results: List[dict], max_tokens: int) -> str:
        """컨텍스트 구성"""
        
        context_parts = []
        token_count = 0
        
        for r in results:
            text = r['text']
            tokens = self._count_tokens(text)
            
            if token_count + tokens > max_tokens:
                break
            
            context_parts.append(f"[출처 {r['chunk_id']}]\n{text}")
            token_count += tokens
        
        return "\n\n".join(context_parts)
    
    async def _generate_answer(self, question: str, context: str) -> str:
        """LLM 답변 생성"""
        
        prompt = f"""
        다음 문서 내용을 바탕으로 질문에 답변하세요.
        
        문서 내용:
        {context}
        
        질문: {question}
        
        답변 규칙:
        - 문서 내용에 근거하여 답변
        - 구체적이고 명확하게
        - 출처 번호는 언급하지 말 것
        - 답변을 모르면 "문서에서 관련 정보를 찾을 수 없습니다"라고 답변
        """
        
        response = await self.llm.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content
```

**의존성**:
- EmbeddingService (임베딩)
- VectorDB (검색)
- OpenAIClient (LLM)
- StateDB (기록 저장)

---

### 4.6 DiagnosisAgent (진단 에이전트)

**책임**: 학습자 수준 진단

**주요 기능**:
1. 퀴즈 결과 분석
2. 레벨 판정 (beginner/intermediate/advanced)
3. 강점/약점 파악
4. 진단 프로필 생성

**입력**:
```python
{
  "task_type": "diagnose_learner",
  "session_id": "abc-123",
  "quiz_id": "quiz-789"
}
```

**출력**:
```python
{
  "status": "success",
  "profile": {
    "score": 80,
    "level": "intermediate",
    "strengths": ["파종", "수확"],
    "weaknesses": ["병충해"],
    "mastery": {
      "파종": 100,
      "물주기": 80,
      "병충해": 40,
      "수확": 90
    }
  },
  "recommendations": [
    "병충해 관리에 대한 추가 학습 권장",
    "실전 사례 중심 학습 추천"
  ]
}
```

**구현**:
```python
class DiagnosisAgent(BaseAgent):
    """학습자 진단 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.state_db = StateDB()
    
    async def execute(self, task: dict) -> dict:
        """진단 실행"""
        
        session_id = task['session_id']
        quiz_id = task['quiz_id']
        
        self.logger.info(f"🔍 Diagnosing learner: {session_id}")
        
        # 1. 퀴즈 결과 조회
        quiz_result = self.state_db.get_quiz_result(quiz_id)
        
        if not quiz_result:
            raise ValueError(f"Quiz result not found: {quiz_id}")
        
        score = quiz_result['score']
        results = quiz_result['results']
        
        # 2. 레벨 판정
        level = self._determine_level(score)
        
        self.logger.info(f"📊 Level: {level} (Score: {score})")
        
        # 3. 개념별 정답률 분석
        concept_mastery = self._analyze_concept_mastery(results)
        
        # 4. 강점/약점 파악
        strengths = [
            concept for concept, rate in concept_mastery.items()
            if rate >= 80
        ]
        
        weaknesses = [
            concept for concept, rate in concept_mastery.items()
            if rate < 60
        ]
        
        # 5. 추천 생성
        recommendations = self._generate_recommendations(
            level=level,
            weaknesses=weaknesses
        )
        
        # 6. 프로필 저장
        profile = {
            "score": score,
            "level": level,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "mastery": concept_mastery,
            "quiz_results": {quiz_id: results}
        }
        
        self.state_db.save_learner_profile(session_id, profile)
        
        self.logger.info(f"✅ Profile saved")
        
        return {
            "status": "success",
            "profile": profile,
            "recommendations": recommendations,
            "processing_time": self._calculate_time()
        }
    
    def _determine_level(self, score: int) -> str:
        """레벨 판정"""
        
        if score >= 71:
            return "advanced"
        elif score >= 41:
            return "intermediate"
        else:
            return "beginner"
    
    def _analyze_concept_mastery(self, results: List[dict]) -> dict:
        """개념별 정답률 분석"""
        
        concept_stats = {}
        
        for r in results:
            concept = r.get('concept', 'unknown')
            
            if concept not in concept_stats:
                concept_stats[concept] = {'correct': 0, 'total': 0}
            
            concept_stats[concept]['total'] += 1
            
            if r['is_correct']:
                concept_stats[concept]['correct'] += 1
        
        # 정답률 계산
        mastery = {
            concept: int((stats['correct'] / stats['total']) * 100)
            for concept, stats in concept_stats.items()
        }
        
        return mastery
    
    def _generate_recommendations(
        self,
        level: str,
        weaknesses: List[str]
    ) -> List[str]:
        """추천 생성"""
        
        recommendations = []
        
        if weaknesses:
            weak_concepts = ', '.join(weaknesses)
            recommendations.append(
                f"{weak_concepts} 개념에 대한 추가 학습 권장"
            )
        
        if level == "beginner":
            recommendations.append("기초 개념 중심의 반복 학습 추천")
        elif level == "intermediate":
            recommendations.append("실전 응용 문제로 심화 학습 추천")
        else:
            recommendations.append("고급 주제 탐구 및 실습 프로젝트 추천")
        
        return recommendations
```

**의존성**:
- StateDB (퀴즈 결과 조회, 프로필 저장)

---

### 4.7 PlanningAgent (학습 계획 에이전트)

**책임**: 맞춤형 학습 계획 생성

**주요 기능**:
1. 진단 프로필 기반 계획
2. 문서 요약 정보 활용
3. 3단계 학습 경로 (기초 → 심화 → 응용)
4. 구체적 가이드라인 제공

**입력**:
```python
{
  "task_type": "create_plan",
  "session_id": "abc-123"
}
```

**출력**:
```python
{
  "status": "success",
  "plan": {
    "level": "intermediate",
    "phases": [
      {
        "phase": "기초",
        "duration": "1-2주",
        "goals": ["기본 개념 이해", "용어 숙지"],
        "activities": [
          "문서 요약 반복 읽기",
          "핵심 개념 노트 정리"
        ],
        "focus_concepts": ["파종", "물주기"]
      },
      {
        "phase": "심화",
        "duration": "2-3주",
        "goals": ["실전 응용", "문제 해결"],
        "activities": [
          "퀴즈 반복 풀이",
          "Q&A로 궁금증 해결",
          "약점 개념 집중 학습"
        ],
        "focus_concepts": ["병충해", "관리"]
      },
      {
        "phase": "응용",
        "duration": "1-2주",
        "goals": ["종합 이해", "실습"],
        "activities": [
          "실제 사례 연구",
          "프로젝트 실습"
        ],
        "focus_concepts": ["종합 관리"]
      }
    ],
    "estimated_total_time": "4-7주"
  }
}
```

**구현**:
```python
class PlanningAgent(BaseAgent):
    """학습 계획 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.state_db = StateDB()
        self.llm = OpenAIClient()
    
    async def execute(self, task: dict) -> dict:
        """학습 계획 생성 실행"""
        
        session_id = task['session_id']
        
        self.logger.info(f"📋 Creating learning plan: {session_id}")
        
        # 1. 진단 프로필 조회
        profile = self.state_db.get_learner_profile(session_id)
        
        if not profile:
            raise ValueError("Profile not found. Run DiagnosisAgent first.")
        
        # 2. 문서 요약 조회
        summary = self.state_db.get_document_summary(session_id)
        
        # 3. 레벨별 템플릿 선택
        template = self._get_template(profile['level'])
        
        # 4. LLM으로 맞춤 계획 생성
        plan = await self._generate_plan_llm(
            profile=profile,
            summary=summary,
            template=template
        )
        
        # 5. 계획 저장
        self.state_db.save_learning_plan(session_id, plan)
        
        self.logger.info(f"✅ Plan created")
        
        return {
            "status": "success",
            "plan": plan,
            "processing_time": self._calculate_time()
        }
    
    def _get_template(self, level: str) -> dict:
        """레벨별 템플릿"""
        
        templates = {
            "beginner": {
                "phases": [
                    {
                        "name": "기초",
                        "duration": "2-3주",
                        "focus": "기본 개념과 용어"
                    },
                    {
                        "name": "심화",
                        "duration": "2-3주",
                        "focus": "개념 간 연결"
                    },
                    {
                        "name": "응용",
                        "duration": "1-2주",
                        "focus": "간단한 실습"
                    }
                ]
            },
            "intermediate": {
                "phases": [
                    {
                        "name": "기초",
                        "duration": "1-2주",
                        "focus": "개념 복습"
                    },
                    {
                        "name": "심화",
                        "duration": "2-3주",
                        "focus": "실전 응용"
                    },
                    {
                        "name": "응용",
                        "duration": "1-2주",
                        "focus": "프로젝트 실습"
                    }
                ]
            },
            "advanced": {
                "phases": [
                    {
                        "name": "기초",
                        "duration": "1주",
                        "focus": "빠른 복습"
                    },
                    {
                        "name": "심화",
                        "duration": "1-2주",
                        "focus": "고급 주제"
                    },
                    {
                        "name": "응용",
                        "duration": "2-3주",
                        "focus": "심화 프로젝트"
                    }
                ]
            }
        }
        
        return templates.get(level, templates['intermediate'])
    
    async def _generate_plan_llm(
        self,
        profile: dict,
        summary: dict,
        template: dict
    ) -> dict:
        """LLM으로 맞춤 계획 생성"""
        
        prompt = f"""
        학습자 프로필:
        - 레벨: {profile['level']}
        - 점수: {profile['score']}
        - 강점: {', '.join(profile['strengths'])}
        - 약점: {', '.join(profile['weaknesses'])}
        
        학습 자료 요약:
        - 주제: {summary['main_topic']}
        - 핵심 개념: {', '.join(summary['key_concepts'])}
        - 난이도: {summary['difficulty_level']}
        
        템플릿:
        {json.dumps(template, ensure_ascii=False, indent=2)}
        
        위 정보를 바탕으로 학습자 맞춤형 3단계 학습 계획을 생성하세요.
        
        요구사항:
        - 약점 개념 집중 보완
        - 구체적인 활동 제시
        - 현실적인 시간 계획
        
        JSON 형식으로 출력:
        {{
          "level": "...",
          "phases": [
            {{
              "phase": "기초",
              "duration": "1-2주",
              "goals": ["...", "..."],
              "activities": ["...", "..."],
              "focus_concepts": ["...", "..."]
            }},
            ...
          ],
          "estimated_total_time": "4-7주"
        }}
        """
        
        response = await self.llm.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
```

**의존성**:
- StateDB (프로필/요약 조회, 계획 저장)
- OpenAIClient (LLM)

---

### 4.8 EvaluationAgent (평가 에이전트)

**책임**: 학습 세션 종합 평가

**주요 기능**:
1. 퀴즈 성적 분석
2. Q&A 활동 분석
3. 학습 시간 추정
4. 종합 피드백 생성

**입력**:
```python
{
  "task_type": "evaluate_session",
  "session_id": "abc-123"
}
```

**출력**:
```python
{
  "status": "success",
  "evaluation": {
    "overall_score": 80,
    "quiz_performance": {
      "total_quizzes": 2,
      "average_score": 78,
      "improvement": "+8"
    },
    "qa_activity": {
      "total_questions": 12,
      "topics_covered": ["파종", "물주기", "병충해"]
    },
    "time_spent": {
      "estimated_minutes": 45,
      "efficiency": "good"
    },
    "feedback": "병충해 관리 부분을 더 학습하시면 좋을 것 같습니다...",
    "next_steps": [
      "약점 개념 복습",
      "실습 프로젝트 시작"
    ]
  }
}
```

**구현**:
```python
class EvaluationAgent(BaseAgent):
    """세션 평가 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.state_db = StateDB()
        self.llm = OpenAIClient()
    
    async def execute(self, task: dict) -> dict:
        """평가 실행"""
        
        session_id = task['session_id']
        
        self.logger.info(f"📊 Evaluating session: {session_id}")
        
        # 1. 데이터 수집
        profile = self.state_db.get_learner_profile(session_id)
        qa_history = self.state_db.get_qa_history(session_id)
        session_info = self.state_db.get_session(session_id)
        
        # 2. 퀴즈 성적 분석
        quiz_performance = self._analyze_quiz_performance(profile)
        
        # 3. Q&A 활동 분석
        qa_activity = self._analyze_qa_activity(qa_history)
        
        # 4. 학습 시간 추정
        time_spent = self._estimate_time_spent(session_info, qa_history)
        
        # 5. 종합 점수
        overall_score = profile['score']
        
        # 6. LLM 피드백 생성
        feedback = await self._generate_feedback(
            profile=profile,
            quiz_performance=quiz_performance,
            qa_activity=qa_activity
        )
        
        # 7. 다음 단계 추천
        next_steps = self._recommend_next_steps(profile)
        
        # 8. 평가 저장
        evaluation = {
            "overall_score": overall_score,
            "quiz_performance": quiz_performance,
            "qa_activity": qa_activity,
            "time_spent": time_spent,
            "feedback": feedback,
            "next_steps": next_steps
        }
        
        self.state_db.save_evaluation(session_id, evaluation)
        
        self.logger.info(f"✅ Evaluation completed")
        
        return {
            "status": "success",
            "evaluation": evaluation,
            "processing_time": self._calculate_time()
        }
    
    def _analyze_quiz_performance(self, profile: dict) -> dict:
        """퀴즈 성적 분석"""
        
        quiz_results = profile.get('quiz_results', {})
        
        if not quiz_results:
            return {
                "total_quizzes": 0,
                "average_score": 0
            }
        
        scores = [
            sum(1 for r in results if r['is_correct']) / len(results) * 100
            for results in quiz_results.values()
        ]
        
        return {
            "total_quizzes": len(quiz_results),
            "average_score": int(sum(scores) / len(scores)),
            "scores": scores,
            "improvement": self._calculate_improvement(scores)
        }
    
    def _analyze_qa_activity(self, qa_history: List[dict]) -> dict:
        """Q&A 활동 분석"""
        
        if not qa_history:
            return {
                "total_questions": 0,
                "topics_covered": []
            }
        
        # 질문에서 주요 키워드 추출 (간단한 방법)
        topics = set()
        for qa in qa_history:
            # TODO: 더 정교한 주제 추출 (NLP)
            words = qa['question'].split()
            topics.update([w for w in words if len(w) > 2])
        
        return {
            "total_questions": len(qa_history),
            "topics_covered": list(topics)[:5]  # 상위 5개
        }
    
    async def _generate_feedback(
        self,
        profile: dict,
        quiz_performance: dict,
        qa_activity: dict
    ) -> str:
        """LLM 피드백 생성"""
        
        prompt = f"""
        학습자 세션 평가:
        
        프로필:
        - 레벨: {profile['level']}
        - 점수: {profile['score']}
        - 약점: {', '.join(profile['weaknesses'])}
        
        퀴즈 성적:
        - 평균: {quiz_performance['average_score']}점
        
        Q&A 활동:
        - 질문 수: {qa_activity['total_questions']}
        
        학습자에게 격려와 함께 구체적인 피드백을 제공하세요.
        (3-4문장, 친근한 어조)
        """
        
        response = await self.llm.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
```

**의존성**:
- StateDB (데이터 조회, 평가 저장)
- OpenAIClient (LLM)

---

### 4.9 RecommendationAgent (자료 추천 에이전트)

**책임**: 추가 학습 자료 추천

**주요 기능**:
1. Wikipedia 검색
2. 주제 관련 문서 추천
3. 약점 개념 보완 자료

**입력**:
```python
{
  "task_type": "recommend_resources",
  "session_id": "abc-123",
  "topic": "토마토 재배"
}
```

**출력**:
```python
{
  "status": "success",
  "recommendations": [
    {
      "source": "Wikipedia",
      "title": "토마토",
      "url": "https://ko.wikipedia.org/wiki/토마토",
      "summary": "토마토는...",
      "relevance": 0.95
    },
    {
      "source": "Wikipedia",
      "title": "가지과",
      "url": "https://ko.wikipedia.org/wiki/가지과",
      "summary": "가지과는...",
      "relevance": 0.78
    }
  ]
}
```

**구현**:
```python
class RecommendationAgent(BaseAgent):
    """자료 추천 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.wikipedia_service = WikipediaService()
        self.state_db = StateDB()
    
    async def execute(self, task: dict) -> dict:
        """자료 추천 실행"""
        
        session_id = task.get('session_id')
        topic = task.get('topic')
        
        self.logger.info(f"📚 Recommending resources for: {topic}")
        
        # 세션 기반 추천
        if session_id:
            profile = self.state_db.get_learner_profile(session_id)
        **의존성**:
- WikipediaService (검색)
- StateDB (프로필 조회, 추천 저장)

---

### 4.10 ConversationAgent (대화 관리 에이전트)

**책임**: Q&A 대화 세션 관리 및 요약

**주요 기능**:
1. 대화 기록 관리
2. 학습 패턴 분석
3. 대화 요약 생성
4. 핵심 학습 내용 추출

**입력**:
```python
{
  "task_type": "summarize_conversation",
  "session_id": "abc-123"
}
```

**출력**:
```python
{
  "status": "success",
  "conversation_summary": {
    "total_questions": 10,
    "duration_minutes": 25,
    "key_learnings": [
      "토마토 물주기는 하루 1-2회",
      "병충해 예방은 통풍이 중요",
      "수확 시기는 색깔로 판단"
    ],
    "new_concepts": [
      "적심",
      "곁순제거",
      "지주대"
    ],
    "review_points": [
      "병충해 증상 구별법 복습 필요",
      "물주기 시기 재확인"
    ],
    "topics_discussed": ["물주기", "병충해", "수확"]
  }
}
```

**구현**:
```python
class ConversationAgent(BaseAgent):
    """대화 관리 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.state_db = StateDB()
        self.llm = OpenAIClient()
    
    async def execute(self, task: dict) -> dict:
        """대화 요약 실행"""
        
        session_id = task['session_id']
        
        self.logger.info(f"💬 Summarizing conversation: {session_id}")
        
        # 1. Q&A 기록 조회
        qa_history = self.state_db.get_qa_history(session_id)
        
        if not qa_history:
            return {
                "status": "no_conversation",
                "message": "대화 기록이 없습니다."
            }
        
        self.logger.info(f"📊 Total Q&A: {len(qa_history)}")
        
        # 2. 대화 시간 계산
        duration = self._calculate_duration(qa_history)
        
        # 3. LLM으로 대화 요약
        summary = await self._summarize_conversation_llm(qa_history)
        
        # 4. 학습 패턴 분석
        patterns = self._analyze_learning_patterns(qa_history)
        
        # 5. 종합 요약
        conversation_summary = {
            "total_questions": len(qa_history),
            "duration_minutes": duration,
            "key_learnings": summary.get('key_learnings', []),
            "new_concepts": summary.get('new_concepts', []),
            "review_points": summary.get('review_points', []),
            "topics_discussed": patterns.get('topics', []),
            "question_types": patterns.get('question_types', {})
        }
        
        # 6. 저장
        self.state_db.save_conversation_summary(session_id, conversation_summary)
        
        self.logger.info(f"✅ Conversation summarized")
        
        return {
            "status": "success",
            "conversation_summary": conversation_summary,
            "processing_time": self._calculate_time()
        }
    
    async def _summarize_conversation_llm(self, qa_history: List[dict]) -> dict:
        """LLM으로 대화 요약"""
        
        # Q&A 포맷팅
        conversation_text = "\n\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}"
            for qa in qa_history
        ])
        
        prompt = f"""
        다음은 학습자와 AI 간의 Q&A 대화입니다.
        
        {conversation_text}
        
        이 대화를 분석하여 다음을 추출하세요:
        
        1. key_learnings: 학습자가 배운 핵심 내용 (3-5개)
        2. new_concepts: 처음 접한 새로운 개념/용어 (3-5개)
        3. review_points: 복습이 필요한 부분 (2-3개)
        
        JSON 형식으로 출력:
        {{
          "key_learnings": ["...", "...", "..."],
          "new_concepts": ["...", "...", "..."],
          "review_points": ["...", "..."]
        }}
        """
        
        response = await self.llm.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _analyze_learning_patterns(self, qa_history: List[dict]) -> dict:
        """학습 패턴 분석"""
        
        # 주제 추출 (간단한 키워드 빈도)
        topics = {}
        
        for qa in qa_history:
            # 질문에서 명사 추출 (간단한 방법)
            words = qa['question'].split()
            for word in words:
                if len(word) > 2:  # 2글자 이상
                    topics[word] = topics.get(word, 0) + 1
        
        # 빈도 순 정렬
        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 질문 유형 분석
        question_types = {
            'what': 0,  # 무엇
            'how': 0,   # 어떻게
            'why': 0,   # 왜
            'when': 0,  # 언제
            'where': 0  # 어디
        }
        
        for qa in qa_history:
            q = qa['question'].lower()
            if '무엇' in q or '뭐' in q:
                question_types['what'] += 1
            elif '어떻게' in q or '방법' in q:
                question_types['how'] += 1
            elif '왜' in q or '이유' in q:
                question_types['why'] += 1
            elif '언제' in q or '시기' in q:
                question_types['when'] += 1
            elif '어디' in q or '위치' in q:
                question_types['where'] += 1
        
        return {
            "topics": [topic for topic, _ in top_topics],
            "question_types": question_types
        }
    
    def _calculate_duration(self, qa_history: List[dict]) -> int:
        """대화 시간 추정 (분)"""
        
        # 간단한 추정: 질문당 2-3분
        return len(qa_history) * 2.5
```

**의존성**:
- StateDB (Q&A 조회, 요약 저장)
- OpenAIClient (LLM)

---

### 4.11 OrchestratorAgent (조율 에이전트) ⭐

**책임**: 에이전트 간 협업 조율 및 워크플로우 관리

**주요 기능**:
1. 작업 분석 및 라우팅
2. 에이전트 호출 순서 결정
3. 에이전트 간 데이터 전달
4. 에러 처리 및 롤백
5. 전체 워크플로우 모니터링

**입력**:
```python
{
  "workflow": "onboard_document",  # 워크플로우 타입
  "params": {
    "file_path": "data/uploads/document.pdf",
    "session_id": "abc-123"
  }
}
```

**출력**:
```python
{
  "status": "success",
  "workflow": "onboard_document",
  "results": {
    "document_processed": {...},
    "summary_generated": {...}
  },
  "execution_time": 15.2,
  "agents_used": ["DocumentAgent", "SummaryAgent"]
}
```

**구현**:
```python
class OrchestratorAgent(BaseAgent):
    """에이전트 조율 전문 에이전트"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        
        # 모든 에이전트 인스턴스 관리
        self.agents = {
            'document': DocumentAgent(config),
            'summary': SummaryAgent(config),
            'quiz': QuizAgent(config),
            'grading': GradingAgent(config),
            'rag': RAGAgent(config),
            'diagnosis': DiagnosisAgent(config),
            'planning': PlanningAgent(config),
            'evaluation': EvaluationAgent(config),
            'recommendation': RecommendationAgent(config),
            'conversation': ConversationAgent(config)
        }
        
        # 워크플로우 정의
        self.workflows = {
            'onboard_document': self._workflow_onboard_document,
            'learning_diagnosis': self._workflow_learning_diagnosis,
            'qa_session': self._workflow_qa_session,
            'session_evaluation': self._workflow_session_evaluation
        }
    
    async def execute(self, task: dict) -> dict:
        """워크플로우 실행"""
        
        workflow = task.get('workflow')
        params = task.get('params', {})
        
        self.logger.info(f"🎯 Starting workflow: {workflow}")
        
        if workflow not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow}")
        
        # 워크플로우 실행
        workflow_func = self.workflows[workflow]
        
        try:
            results = await workflow_func(params)
            
            self.logger.info(f"✅ Workflow completed: {workflow}")
            
            return {
                "status": "success",
                "workflow": workflow,
                "results": results,
                "execution_time": self._calculate_time(),
                "agents_used": results.get('agents_used', [])
            }
        
        except Exception as e:
            self.logger.error(f"❌ Workflow failed: {e}")
            
            return {
                "status": "failed",
                "workflow": workflow,
                "error": str(e)
            }
    
    async def _workflow_onboard_document(self, params: dict) -> dict:
        """워크플로우: 문서 온보딩"""
        
        agents_used = []
        
        # Step 1: DocumentAgent - 문서 처리
        self.logger.info("📄 Step 1: Processing document...")
        
        doc_result = await self.agents['document'].execute({
            "task_type": "process_document",
            "file_path": params['file_path'],
            "session_id": params['session_id']
        })
        agents_used.append('DocumentAgent')
        
        if doc_result['status'] != 'success':
            raise Exception("Document processing failed")
        
        # Step 2: SummaryAgent - 요약 생성
        self.logger.info("📝 Step 2: Generating summary...")
        
        summary_result = await self.agents['summary'].execute({
            "task_type": "summarize_document",
            "session_id": params['session_id'],
            "summary_type": "balanced"
        })
        agents_used.append('SummaryAgent')
        
        if summary_result['status'] != 'success':
            raise Exception("Summary generation failed")
        
        return {
            "document_processed": doc_result,
            "summary_generated": summary_result,
            "agents_used": agents_used
        }
    
    async def _workflow_learning_diagnosis(self, params: dict) -> dict:
        """워크플로우: 학습 진단"""
        
        agents_used = []
        session_id = params['session_id']
        
        # Step 1: QuizAgent - 퀴즈 생성
        self.logger.info("📝 Step 1: Generating quiz...")
        
        quiz_result = await self.agents['quiz'].execute({
            "task_type": "generate_quiz",
            "session_id": session_id,
            "num_questions": 5
        })
        agents_used.append('QuizAgent')
        
        quiz_id = quiz_result['quiz_id']
        
        # Step 2: 사용자 답안 대기 (실제로는 API 호출 분리)
        # 여기서는 시뮬레이션
        user_answers = params.get('answers', [1, 0, 2, 1, 3])
        
        # Step 3: GradingAgent - 채점
        self.logger.info("📊 Step 2: Grading quiz...")
        
        grading_result = await self.agents['grading'].execute({
            "task_type": "grade_quiz",
            "quiz_id": quiz_id,
            "answers": user_answers
        })
        agents_used.append('GradingAgent')
        
        # Step 4: DiagnosisAgent - 진단
        self.logger.info("🔍 Step 3: Diagnosing learner...")
        
        diagnosis_result = await self.agents['diagnosis'].execute({
            "task_type": "diagnose_learner",
            "session_id": session_id,
            "quiz_id": quiz_id
        })
        agents_used.append('DiagnosisAgent')
        
        # Step 5: PlanningAgent - 학습 계획
        self.logger.info("📋 Step 4: Creating learning plan...")
        
        planning_result = await self.agents['planning'].execute({
            "task_type": "create_plan",
            "session_id": session_id
        })
        agents_used.append('PlanningAgent')
        
        return {
            "quiz_generated": quiz_result,
            "quiz_graded": grading_result,
            "learner_diagnosed": diagnosis_result,
            "plan_created": planning_result,
            "agents_used": agents_used
        }
    
    async def _workflow_qa_session(self, params: dict) -> dict:
        """워크플로우: Q&A 세션"""
        
        agents_used = []
        session_id = params['session_id']
        question = params['question']
        
        # Step 1: RAGAgent - 질문 답변
        self.logger.info(f"❓ Answering question: {question}")
        
        rag_result = await self.agents['rag'].execute({
            "task_type": "answer_question",
            "session_id": session_id,
            "question": question
        })
        agents_used.append('RAGAgent')
        
        return {
            "answer_generated": rag_result,
            "agents_used": agents_used
        }
    
    async def _workflow_session_evaluation(self, params: dict) -> dict:
        """워크플로우: 세션 종합 평가"""
        
        agents_used = []
        session_id = params['session_id']
        
        # Step 1: ConversationAgent - 대화 요약
        self.logger.info("💬 Step 1: Summarizing conversation...")
        
        conversation_result = await self.agents['conversation'].execute({
            "task_type": "summarize_conversation",
            "session_id": session_id
        })
        agents_used.append('ConversationAgent')
        
        # Step 2: EvaluationAgent - 종합 평가
        self.logger.info("📊 Step 2: Evaluating session...")
        
        evaluation_result = await self.agents['evaluation'].execute({
            "task_type": "evaluate_session",
            "session_id": session_id
        })
        agents_used.append('EvaluationAgent')
        
        # Step 3: RecommendationAgent - 자료 추천
        self.logger.info("📚 Step 3: Recommending resources...")
        
        recommendation_result = await self.agents['recommendation'].execute({
            "task_type": "recommend_resources",
            "session_id": session_id
        })
        agents_used.append('RecommendationAgent')
        
        return {
            "conversation_summarized": conversation_result,
            "session_evaluated": evaluation_result,
            "resources_recommended": recommendation_result,
            "agents_used": agents_used
        }
    
    def get_agent(self, agent_name: str) -> BaseAgent:
        """에이전트 조회"""
        return self.agents.get(agent_name)
    
    def register_agent(self, name: str, agent: BaseAgent):
        """새 에이전트 등록 (확장성)"""
        self.agents[name] = agent
        self.logger.info(f"✅ Agent registered: {name}")
```

**의존성**:
- 모든 에이전트 (10개)

---

## 5. 핵심 기능 명세

### 5.1 문서 즉시 요약 (SummaryAgent) ⭐

**사용자 스토리**:
> "PDF를 업로드하면 자동으로 3줄 요약을 보여준다"

**처리 흐름**:
```
1. 사용자: PDF 업로드
2. OrchestratorAgent → DocumentAgent: 문서 처리
3. DocumentAgent: 텍스트 추출, 청킹, 임베딩
4. OrchestratorAgent → SummaryAgent: 요약 생성
5. SummaryAgent:
   - 캐시 확인 (있으면 즉시 반환)
   - 토큰 수 계산
   - < 3000: 직접 요약
   - ≥ 3000: Map-Reduce
   - 품질 평가
   - 캐시 & DB 저장
6. 사용자: 요약 결과 표시
```

**UI 예시**:
```python
# Streamlit
st.title("📄 문서 요약")

uploaded_file = st.file_uploader("PDF 업로드", type=['pdf'])

if uploaded_file:
    with st.spinner("문서 처리 중..."):
        # 업로드 & 자동 요약
        result = api_client.upload_and_summarize(uploaded_file)
    
    st.success("✅ 처리 완료!")
    
    # 요약 카드
    with st.container():
        st.subheader("📝 문서 요약")
        
        # TL;DR
        st.markdown("**핵심 요약 (TL;DR)**")
        for i, point in enumerate(result['summary']['tldr'], 1):
            st.write(f"{i}. {point}")
        
        st.divider()
        
        # 메타 정보
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("주제", result['summary']['main_topic'])
        
        with col2:
            st.metric("난이도", result['summary']['difficulty_level'])
        
        with col3:
            st.metric("예상 시간", f"{result['summary']['estimated_time_minutes']}분")
        
        # 핵심 개념
        st.markdown("**핵심 개념**")
        st.write(", ".join(result['summary']['key_concepts']))
```

---

### 5.2 RAG 기반 Q&A (RAGAgent) ⭐

**사용자 스토리**:
> "문서 내용에 대해 자유롭게 질문하고 답변을 받는다"

**처리 흐름**:
```
1. 사용자: 질문 입력
2. OrchestratorAgent → RAGAgent: 답변 요청
3. RAGAgent:
   - 질문 임베딩
   - ChromaDB 검색 (Top-5)
   - 유사도 필터링 (> 0.7)
   - 컨텍스트 구성
   - LLM 답변 생성
   - ConversationAgent에 기록
4. 사용자: 답변 & 출처 표시
```

**UI 예시**:
```python
# Streamlit
st.title("💬 Q&A 채팅")

# 채팅 기록
for qa in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(qa['question'])
    
    with st.chat_message("assistant"):
        st.write(qa['answer'])
        
        # 출처 표시
        with st.expander("📚 출처 보기"):
            for source in qa['sources']:
                st.caption(f"[{source['chunk_id']}] {source['text']} (유사도: {source['similarity']})")

# 입력
question = st.chat_input("질문을 입력하세요...")

if question:
    # 질문 표시
    with st.chat_message("user"):
        st.write(question)
    
    # 답변 생성
    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            result = api_client.ask_question(
                session_id=session_id,
                question=question
            )
        
        st.write(result['answer'])
        
        with st.expander("📚 출처 보기"):
            for source in result['sources']:
                st.caption(f"[{source['chunk_id']}] {source['text']}")
    
    # 기록 저장
    st.session_state.chat_history.append({
        'question': question,
        'answer': result['answer'],
        'sources': result['sources']
    })
```

---

### 5.3 학습 진단 퀴즈 (QuizAgent + GradingAgent + DiagnosisAgent)

**사용자 스토리**:
> "퀴즈를 풀어 내 수준을 파악하고 맞춤 계획을 받는다"

**처리 흐름**:
```
1. 사용자: "진단 시작" 버튼
2. OrchestratorAgent: workflow_learning_diagnosis 실행
3. QuizAgent: 5문항 생성
4. 사용자: 퀴즈 풀이
5. GradingAgent: 채점
6. DiagnosisAgent: 레벨 판정
7. PlanningAgent: 학습 계획 생성
8. 사용자: 종합 결과 표시
```

**UI 예시**:
```python
# 진단 페이지
st.title("🎯 학습 수준 진단")

if 'quiz' not in st.session_state:
    # 퀴즈 생성
    if st.button("🎯 진단 시작", type="primary"):
        with st.spinner("퀴즈 생성 중..."):
            quiz = api_client.generate_quiz(session_id)
        
        st.session_state.quiz = quiz
        st.session_state.answers = [None] * len(quiz['questions'])

else:
    quiz = st.session_state.quiz
    
    # 퀴즈 표시
    for idx, q in enumerate(quiz['questions']):
        st.subheader(f"Q{idx+1}. {q['question']}")
        
        answer = st.radio(
            "답을 선택하세요:",
            options=q['options'],
            key=f"q_{idx}",
            index=None
        )
        
        if answer:
            st.session_state.answers[idx] = q['options'].index(answer)
        
        st.divider()
    
    # 제출
    if st.button("📝 제출하기", type="primary"):
        if None in st.session_state.answers:
            st.warning("⚠️ 모든 문제를 풀어주세요")
        else:
            with st.spinner("채점 중..."):
                # 채점 + 진단 + 계획 (워크플로우)
                result = api_client.complete_diagnosis(
                    session_id=session_id,
                    quiz_id=quiz['quiz_id'],
                    answers=st.session_state.answers
                )
            
            # 결과 표시
            st.success(f"✅ 점수: {result['score']}/100")
            
            st.subheader("📊 진단 결과")
            st.metric("레벨", result['profile']['level'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**강점**")
                for s in result['profile']['strengths']:
                    st.write(f"✅ {s}")
            
            with col2:
                st.write("**약점**")
                for w in result['profile']['weaknesses']:
                    st.write(f"⚠️ {w}")
            
            # 학습 계획
            st.subheader("📋 맞춤 학습 계획")
            
            for phase in result['plan']['phases']:
                with st.expander(f"{phase['phase']} ({phase['duration']})"):
                    st.write(f"**목표:** {', '.join(phase['goals'])}")
                    st.write(f"**활동:**")
                    for activity in phase['activities']:
                        st.write(f"- {activity}")
```

---

### 5.4 대화 세션 요약 (ConversationAgent)

**사용자 스토리**:
> "Q&A를 여러 번 한 후 '지금까지 요약' 버튼을 누르면 학습 내용이 정리된다"

**처리 흐름**:
```
1. 사용자: 5-10회 Q&A
2. 사용자: "지금까지 요약" 버튼
3. OrchestratorAgent → ConversationAgent: 대화 요약
4. ConversationAgent:
   - Q&A 기록 조회
   - LLM으로 핵심 내용 추출
   - 학습 패턴 분석
   - 요약 생성
5. 사용자: 요약 표시
```

**UI 예시**:
```python
# Q&A 페이지
st.title("💬 Q&A 채팅")

# ... (채팅 UI)

# 대화 요약 버튼
if len(st.session_state.chat_history) >= 3:
    if st.button("📝 지금까지 요약"):
        with st.spinner("대화 요약 생성 중..."):
            summary = api_client.summarize_conversation(session_id)
        
        st.subheader("💡 학습 요약")
        
        # 핵심 학습 내용
        st.markdown("**핵심 학습 내용**")
        for learning in summary['key_learnings']:
            st.write(f"✅ {learning}")
        
        st.divider()
        
        # 새로운 개념
        st.markdown("**새로 배운 개념**")
        for concept in summary['new_concepts']:
            st.write(f"🆕 {concept}")
        
        st.divider()
        
        # 복습 포인트
        st.markdown("**복습 필요 사항**")
        for point in summary['review_points']:
            st.write(f"📌 {point}")
        
        st.divider()
        
        # 통계
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("총 질문 수", summary['total_questions'])
        
        with col2:
            st.metric("학습 시간", f"{summary['duration_minutes']}분")
```

---

### 5.5 자료 추천 (RecommendationAgent)

**사용자 스토리**:
> "추가로 공부할 자료를 추천받는다"

**처리 흐름**:
```
1. 사용자: "추가 자료 보기" 또는 자동 추천
2. OrchestratorAgent → RecommendationAgent: 추천 요청
3. RecommendationAgent:
   - 프로필 조회 (약점 파악)
   - Wikipedia 검색
   - 관련 문서 3-5개 추천
4. 사용자: 추천 자료 표시
```

**UI 예시**:
```python
# 자료 추천 페이지
st.title("📚 추가 학습 자료")

if st.button("🔍 자료 추천받기"):
    with st.spinner("자료 검색 중..."):
        recommendations = api_client.get_recommendations(session_id)
    
    st.subheader("추천 자료")
    
    for rec in recommendations:
        with st.expander(f"📖 {rec['title']}"):
            st.write(rec['summary'])
            st.write(f"**출처:** {rec['source']}")
            st.link_button("자세히 보기 →", rec['url'])
```

---

## 6. 기술 스택

### 6.1 Backend
```txt
# Core
python==3.10.0
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# AI & ML
openai==1.54.0
tiktoken==0.5.1

# Database
chromadb==0.4.22
aiosqlite==0.19.0

# PDF & Text
pymupdf==1.26.5

# Utils
tenacity==8.2.3          # 재시도
python-multipart==0.0.6  # 파일 업로드
python-dotenv==1.0.0     # 환경 변수

# Wikipedia
wikipedia-api==0.6.0

# Monitoring
python-json-logger==2.0.7
```

### 6.2 Frontend
```txt
streamlit==1.31.0
requests==2.31.0
plotly==5.18.0           # 차트 (선택)
```

### 6.3 Development
```txt
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.12.0
flake8==6.1.0
mypy==1.7.1
```

---

## 7. 데이터 모델

### 7.1 SQLite 스키마
```sql
-- 학습 세션
CREATE TABLE learning_sessions (
    session_id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 문서 요약
CREATE TABLE document_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    tldr TEXT NOT NULL,
    main_topic TEXT NOT NULL,
    key_concepts TEXT NOT NULL,  -- JSON array
    difficulty_level TEXT NOT NULL,
    estimated_time_minutes INTEGER NOT NULL,
    quality_score REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- 퀴즈
CREATE TABLE quizzes (
    quiz_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    questions TEXT NOT NULL,  -- JSON array
    total_score INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- 퀴즈 결과
CREATE TABLE quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    score INTEGER NOT NULL,
    percentage REAL NOT NULL,
    correct_count INTEGER NOT NULL,
    wrong_count INTEGER NOT NULL,
    results TEXT NOT NULL,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- 학습자 프로필
CREATE TABLE learner_profiles (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    score INTEGER NOT NULL,
    level TEXT NOT NULL,
    strengths TEXT,  -- JSON array
    weaknesses TEXT,  -- JSON array
    mastery TEXT,  -- JSON object
    quiz_results TEXT,  -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- 학습 계획
CREATE TABLE learning_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    level TEXT NOT NULL,
    phases TEXT NOT NULL,  -- JSON array
    estimated_total_time TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- Q&A 기록
CREATE TABLE qa_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- 대화 요약
CREATE TABLE conversation_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    duration_minutes INTEGER NOT NULL,
    key_learnings TEXT NOT NULL,  -- JSON array
    new_concepts TEXT NOT NULL,  -- JSON array
    review_points TEXT NOT NULL,  -- JSON array
    topics_discussed TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- 세션 평가
CREATE TABLE session_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    overall_score INTEGER NOT NULL,
    quiz_performance TEXT NOT NULL,  -- JSON object
    qa_activity TEXT NOT NULL,  -- JSON object
    time_spent TEXT NOT NULL,  -- JSON object
    feedback TEXT NOT NULL,
    next_steps TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- 자료 추천
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    recommendations TEXT NOT NULL,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

-- 인덱스
CREATE INDEX idx_sessions_created ON learning_sessions(created_at);
CREATE INDEX idx_qa_session ON qa_history(session_id, created_at);
CREATE INDEX idx_quiz_session ON quizzes(session_id);
```

---

## 8. API 설계

### 8.1 엔드포인트 목록
```python
# 문서 관리
POST   /api/upload                        # 업로드 + 자동 요약
GET    /api/sessions/{session_id}         # 세션 정보 조회

# 요약
GET    /api/summary/document/{session_id} # 문서 요약 조회
POST   /api/summary/conversation           # 대화 요약 생성

# 퀴즈 & 진단
POST   /api/diagnosis/{session_id}        # 퀴즈 생성
POST   /api/diagnosis/submit               # 퀴즈 제출 + 채점 + 진단 + 계획

# Q&A
POST   /api/ask                            # 질문 답변

# 학습 계획
GET    /api/plan/{session_id}              # 학습 계획 조회

# 평가 & 추천
POST   /api/evaluation/{session_id}       # 세션 평가
GET    /api/recommendations/{session_id}  # 자료 추천

# 헬스체크
GET    /api/health                         # 서버 상태
```

### 8.2 API 상세

#### POST /api/upload
```python
# Request
Content-Type: multipart/form-data
{
  "file": <PDF file>
}

# Response
{
  "status": "success",
  "session_id": "abc-123",
  "file_name": "document.pdf",
  "summary": {
    "tldr": [...],
    "main_topic": "...",
    "key_concepts": [...],
    "difficulty_level": "intermediate",
    "estimated_time_minutes": 120,
    "quality_score": 0.85
  },
  "processing_time": 12.5
}
```

#### POST /api/diagnosis/submit
```python
# Request
{
  "session_id": "abc-123",
  "quiz_id": "quiz-789",
  "answers": [1, 0, 2, 1, 3]
}

# Response
{
  "status": "success",
  "grading": {
    "score": 80,
    "results": [...]
  },
  "diagnosis": {
    "level": "intermediate",
    "strengths": [...],
    "weaknesses": [...]
  },
  "plan": {
    "phases": [...]
  }
}
```

#### POST /api/ask
```python
# Request
{
  "session_id": "abc-123",
  "question": "토마토 물주기 주기는?"
}

# Response
{
  "status": "success",
  "question": "...",
  "answer": "...",
  "sources": [...]
}
```

---

## 9. 개발 로드맵

### 📅 Day 1-2: 에이전트 시스템 설계 (16h)

**Day 1 (8h)**: BaseAgent + 기본 구조
- BaseAgent 추상 클래스
- OrchestratorAgent 골격
- StateDB 클래스
- 설정 관리

**Day 2 (8h)**: 핵심 에이전트 3개
- DocumentAgent (완성)
- SummaryAgent (완성)
- RAGAgent (완성)

---

### 📅 Day 3-4: 진단 & 평가 에이전트 (16h)

**Day 3 (8h)**:
- QuizAgent
- GradingAgent
- DiagnosisAgent

**Day 4 (8h)**:
- PlanningAgent
- EvaluationAgent
- 워크플로우 테스트

---

### 📅 Day 5: 대화 & 추천 에이전트 (8h)

- ConversationAgent
- RecommendationAgent
- OrchestratorAgent 워크플로우 완성
- 통합 테스트

---

### 📅 Day 6: API 레이어 (8h)

- FastAPI 엔드포인트 (10개)
- Pydantic 모델
- 에러 핸들링
- API 문서 (Swagger)

---

### 📅 Day 7-8: Frontend (16h)

**Day 7 (8h)**:
- 홈 (업로드 + 요약)
- Q&A 페이지
- 진단 페이지 (퀴즈)

**Day 8 (8h)**:
- 대시보드
- 학습 계획 페이지
- 추가 자료 페이지
- 사이드바 & 네비게이션

---

### 📅 Day 9: 통합 테스트 & 최적화 (8h)

- E2E 테스트
- 성능 최적화
- 캐싱 검증
- 에러 시나리오

---

### 📅 Day 10: 문서화 & 시연 준비 (8h)

- README.md
- API 문서
- 아키텍처 다이어그램
- 시연 시나리오
- 발표 자료

---

## 10. 성공 지표

### 10.1 기능 달성 (학원 요구사항)

✅ **문서 요약**: 100%
- 즉시 요약 생성
- 품질 점수 0.7+
- 처리 시간 <10초

✅ **Q&A**: 100%
- RAG 기반 답변
- 유사도 0.7+ 필터링
- 응답 시간 <5초

✅ **문제 생성**: 100%
- 객관식 5문항
- 자동 생성
- 핵심 개념 반영

✅ **자료 추천**: 100%
- Wikipedia 연동
- 상위 3개 추천

### 10.2 에이전트 시스템 (고급 목표)

✅ **10개 에이전트**: 100%
- 각 에이전트 단일 책임
- 느슨한 결합
- 확장 가능

✅ **워크플로우**: 100%
- 4개 주요 워크플로우
- 에이전트 조율
- 에러 처리

✅ **성능**:
- 캐싱 효과: 90%+
- 전체 처리: 20초 이내
- 동시 사용자: 10명 (MVP)

---

## 11. 비용 예산

### 11.1 100명/월 기준
```
OpenAI API 비용:

1. 임베딩 (text-embedding-3-small: $0.02 / 1M tokens)
   - 문서당 평균 3,000 토큰
   - 100명 × 1문서 = 300,000 토큰
   - 비용: $0.006 × 100 = $0.60

2. 문서 요약 (gpt-4o-mini: $0.15 / 1M input, $0.60 / 1M output)
   - Map-Reduce: 입력 5,000 + 출력 500 토큰
   - 비용: ($0.15×5 + $0.60×0.5) / 1000 = $0.001
   - 100명: $0.10
   - 캐싱 후: $0.01 (90% 절감)

3. 퀴즈 생성 (gpt-4o-mini)
   - 입력 2,000 + 출력 1,000 토큰
   - 비용: $0.0006
   - 100명 × 2회: $0.12

4. Q&A (gpt-4o-mini)
   - 입력 3,000 + 출력 500 토큰
   - 비용: $0.0008
   - 100명 × 10질문: $0.80

5. 기타 LLM (피드백, 계획 등)
   - 100명: $0.50

총 예상 비용: $2.13/월
사용자당: $0.021

매우 저렴! ✅
```

### 11.2 비용 최적화

1. **캐싱**: 요약 90% 절감
2. **gpt-4o-mini**: gpt-4 대비 15배 저렴
3. **임베딩 재사용**: 문서당 1회만
4. **배치 처리**: API 호출 최소화

---

## 12. 확장 계획

### 12.1 v2.0 고급 (Phase 2)

**추가 에이전트 후보**:
- **ShortAnswerGradingAgent**: 단답형 AI 채점
- **EssayGradingAgent**: 주관식 AI 채점
- **OCRFallbackAgent**: Google Vision 연동
- **AnalyticsAgent**: 학습 패턴 심화 분석

**고급 기능**:
- 다양한 퀴즈 유형 (단답형, O/X, 주관식)
- Perplexity 스타일 답변없음 처리
- 맞춤형 요약 (사용자 지시)
- 비용 모니터링 대시보드

---

### 12.2 v3.0 차세대 (Phase 3)

**음성 인터페이스**:
- TTS (요약 음성 읽기)
- STT (음성 질문)
- 팟캐스트 스타일 대화 요약

**멀티모달**:
- 이미지/도표 분석 (GPT-4 Vision)
- YouTube 자막 처리
- PPT 변환

---

## 13. 폴더 구조
```
SynapseSimple/
├── backend/
│   ├── agents/                          # 10개 에이전트 ⭐
│   │   ├── base_agent.py
│   │   ├── orchestrator_agent.py        # 조율
│   │   ├── document_agent.py
│   │   ├── summary_agent.py
│   │   ├── quiz_agent.py
│   │   ├── grading_agent.py
│   │   ├── rag_agent.py
│   │   ├── diagnosis_agent.py
│   │   ├── planning_agent.py
│   │   ├── evaluation_agent.py
│   │   ├── recommendation_agent.py
│   │   └── conversation_agent.py
│   ├── services/                        # 공통 서비스
│   │   ├── ocr_service.py
│   │   ├── embedding_service.py
│   │   ├── wikipedia_service.py
│   │   └── openai_client.py
│   ├── db/                              # 데이터 저장
│   │   ├── schema.sql
│   │   ├── state_db.py                  # SQLite
│   │   └── vector_db.py                 # ChromaDB
│   ├── utils/                           # 유틸리티
│   │   ├── text_processor.py
│   │   ├── summary_cache.py
│   │   ├── file_validator.py
│   │   └── logger.py
│   ├── api/                             # API 레이어
│   │   ├── routes/
│   │   │   ├── document.py
│   │   │   ├── summary.py
│   │   │   ├── diagnosis.py
│   │   │   ├── qa.py
│   │   │   └── evaluation.py
│   │   └── models.py                    # Pydantic
│   ├── config.py
│   └── main.py                          # FastAPI app
├── frontend/                            # Streamlit
│   ├── pages/
│   │   ├── 1_Home.py                    # 업로드 + 요약
│   │   ├── 2_Diagnosis.py               # 퀴즈
│   │   ├── 3_QA.py                      # 채팅
│   │   ├── 4_Dashboard.py               # 대시보드
│   │   ├── 5_Plan.py                    # 학습 계획
│   │   └── 6_Resources.py               # 추가 자료
│   ├── components/
│   │   ├── summary_card.py
│   │   ├── quiz_display.py
│   │   └── chat_interface.py
│   ├── utils/
│   │   └── api_client.py
│   └── app.py                           # Main app
├── prompts/                             # LLM 프롬프트
│   ├── summary_prompts.py
│   ├── quiz_prompts.py
│   ├── diagnosis_prompts.py
│   └── planning_prompts.py
├── tests/                               # 테스트
│   ├── test_agents/
│   ├── test_services/
│   └── test_api/
├── data/
│   ├── uploads/                         # PDF 저장
│   ├── chroma/                          # ChromaDB
│   └── cache/                           # 캐시
├── docs/                                # 문서
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── AGENTS.md
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.sh                               # 실행 스크립트
```

---

## 14. 시연 시나리오

### 시나리오: 토마토 재배 학습 지원

**참가자**: 초보 농업인

**1단계: 문서 업로드 (2분)**
```
1. 사용자: "토마토_재배_가이드.pdf" 업로드
2. 시스템: 
   - DocumentAgent: 텍스트 추출, 청킹, 임베딩
   - SummaryAgent: 요약 자동 생성
3. 화면:
   📝 문서 요약
   TL;DR:
   1. 토마토는 4월에 파종하는 것이 적기입니다
   2. 하루 1-2회 적절한 물주기가 중요합니다
   3. 병충해 예방을 위해 통풍 관리가 필수입니다
   
   주제: 토마토 재배 가이드
   난이도: 중급
   예상 학습 시간: 120분
   핵심 개념: 파종, 물주기, 병충해, 지주대, 수확
```

**2단계: 학습 수준 진단 (5분)**
```
1. 사용자: "진단 시작" 버튼 클릭
2. 시스템:
   - QuizAgent: 5문항 객관식 생성
3. 사용자: 퀴즈 풀이
   Q1. 토마토 파종 적기는? → 4월 선택 ✅
   Q2. 물주기 주기는? → 오답 ❌
   Q3. 병충해 예방법은? → 정답 ✅
   Q4. 지주대 설치 시기는? → 오답 ❌
   Q5. 수확 판단 기준은? → 정답 ✅
4. 시스템:
   - GradingAgent: 채점 (60/100)
   - DiagnosisAgent: 레벨 판정 (중급)
   - PlanningAgent: 학습 계획 생성
5. 화면:
   📊 진단 결과
   점수: 60/100
   레벨: 중급 (Intermediate)
   
   강점: 파종, 수확
   약점: 물주기, 지주대
   
   📋 맞춤 학습 계획
   
   기초 (1-2주):
   - 물주기 개념 복습
   - 지주대 설치 방법 학습
   
   심화 (2-3주):
   - 실전 물주기 타이밍
   - 다양한 지주대 유형
   
   응용 (1-2주):
   - 실습 프로젝트
```

**3단계: Q&A 학습 (10분)**
```
1. 사용자: "토마토 물주기를 언제 하는 게 좋나요?"
2. 시스템:
   - RAGAgent: ChromaDB 검색 + LLM 답변
3. 화면:
   💬 답변:
   토마토 물주기는 이른 아침이나 저녁이 가장 좋습니다.
   한낮의 강한 햇볕 아래에서는 피하세요.
   토양 표면이 건조해졌을 때 충분히 주되,
   과습은 피해야 합니다.
   
   📚 출처:
   [청크 3] "물주기는 이른 아침..." (유사도: 0.92)
   [청크 7] "토양 습도 확인..." (유사도: 0.85)

(5-10회 반복)

4. 사용자: "지금까지 요약" 버튼
5. 시스템:
   - ConversationAgent: 대화 요약 생성
6. 화면:
   💡 학습 요약
   
   핵심 학습 내용:
   ✅ 물주기는 아침/저녁에 수행
   ✅ 토양 건조 상태 확인 필요
   ✅ 지주대는 30cm 높이에 설치
   
   새로 배운 개념:
   🆕 적심 (곁순 제거)
   🆕 배수 관리
   
   복습 필요:
   📌 물주기 타이밍 재확인
   📌 지주대 설치 높이 암기
```

**4단계: 종합 평가 & 추가 자료 (3분)**
```
1. 시스템:
   - EvaluationAgent: 세션 종합 평가
   - RecommendationAgent: 추가 자료 추천
2. 화면:
   📊 종합 평가
   
   퀴즈 성적: 60점
   Q&A 활동: 8개 질문
   학습 시간: 약 25분
   
   피드백:
   물주기와 지주대 관련 질문이 많았네요.
   약점 개념을 잘 보완하고 계십니다!
   실제 텃밭에서 실습해보시면 더 좋을 것 같아요.
   
   다음 단계:
   • 물주기 실습 (실제 적용)
   • 지주대 설치 영상 시청
   
   📚 추가 학습 자료
   
   1. [Wikipedia] 토마토
      "토마토는 가지과에 속하는..."
      → 자세히 보기
   
   2. [Wikipedia] 가지과 작물
      "가지과 식물의 공통 특징..."
      → 자세히 보기
```

---

## 15. 참고 자료

- **v1.0 완료 보고서**: PROJECT_COMPLETE_V1.md
- **최초 계획서**: 시냅스 개발 계획서 v6.0 FINAL.pdf
- **에이전트 패턴**: https://www.anthropic.com/research/building-effective-agents
- **RAG Best Practices**: https://docs.llamaindex.ai/en/stable/

---

## 16. 부록

### A. BaseAgent 인터페이스
```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
import time

class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스
    
    모든 에이전트는 이 클래스를 상속받아야 합니다.
    
    주요 원칙:
    1. 단일 책임: 하나의 핵심 기능만 수행
    2. 상태 무저장: 에이전트 자체는 상태를 가지지 않음
    3. 표준 인터페이스: execute() 메서드 구현 필수
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 에이전트 설정 딕셔너리
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._start_time = None
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """에이전트 실행 (필수 구현)
        
        Args:
            task: 작업 정보
                - task_type: 작업 유형 (str)
                - 기타 파라미터
        
        Returns:
            결과 딕셔너리:
                - status: "success" | "failed"
                - 기타 결과 데이터
        
        Raises:
            Exception: 실행 실패 시
        """
        pass
    
    def validate_input(self, task: Dict[str, Any]) -> bool:
        """입력 검증
        
        Args:
            task: 작업 정보
        
        Returns:
            유효성 여부
        """
        required_fields = ['task_type']
        
        for field in required_fields:
            if field not in task:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def log_execution(self, task: Dict[str, Any], result: Dict[str, Any]):
        """실행 로깅
        
        Args:
            task: 작업 정보
            result: 실행 결과
        """
        self.logger.info(
            f"Executed {task.get('task_type')} - "
            f"Status: {result.get('status')} - "
            f"Time: {result.get('processing_time', 0):.2f}s"
        )
    
    def _start_timer(self):
        """타이머 시작"""
        self._start_time = time.time()
    
    def _calculate_time(self) -> float:
        """처리 시간 계산
        
        Returns:
            경과 시간 (초)
        """
        if self._start_time is None:
            return 0.0
        
        return time.time() - self._start_time
    
    def _count_tokens(self, text: str) -> int:
        """토큰 수 계산
        
        Args:
            text: 텍스트
        
        Returns:
            토큰 수
        """
        import tiktoken
        
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(text))
```

---

### B. 에이전트 추가 가이드

**새로운 에이전트를 추가하는 방법**:

1. **에이전트 클래스 생성**
```python
# backend/agents/new_agent.py

from agents.base_agent import BaseAgent
from typing import Dict, Any

class NewAgent(BaseAgent):
    """새로운 에이전트 설명"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 필요한 서비스 초기화
        self.service = SomeService()
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """실행 로직"""
        
        self._start_timer()
        
        # 입력 검증
        if not self.validate_input(task):
            return {"status": "failed", "error": "Invalid input"}
        
        try:
            # 1. 데이터 조회
            data = self._get_data(task)
            
            # 2. 처리
            result = await self._process(data)
            
            # 3. 저장
            self._save_result(result)
            
            # 4. 응답
            return {
                "status": "success",
                "result": result,
                "processing_time": self._calculate_time()
            }
        
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _get_data(self, task: Dict[str, Any]) -> Any:
        """데이터 조회"""
        pass
    
    async def _process(self, data: Any) -> Any:
        """처리 로직"""
        pass
    
    def _save_result(self, result: Any):
        """결과 저장"""
        pass
```

2. **OrchestratorAgent에 등록**
```python
# backend/agents/orchestrator_agent.py

class OrchestratorAgent(BaseAgent):
    
    def __init__(self, config: dict):
        super().__init__(config)
        
        self.agents = {
            # 기존 에이전트...
            'new': NewAgent(config),  # 추가
        }
```

3. **워크플로우에 통합**
```python
async def _workflow_new_feature(self, params: dict) -> dict:
    """새 워크플로우"""
    
    agents_used = []
    
    # NewAgent 사용
    new_result = await self.agents['new'].execute({
        "task_type": "new_task",
        "param1": params['param1']
    })
    agents_used.append('NewAgent')
    
    return {
        "new_result": new_result,
        "agents_used": agents_used
    }
```

4. **API 엔드포인트 추가**
```python
# backend/api/routes/new_feature.py

from fastapi import APIRouter

router = APIRouter(prefix="/api/new", tags=["new"])

@router.post("/")
async def new_feature(request: NewRequest):
    """새 기능"""
    
    orchestrator = OrchestratorAgent(config)
    
    result = await orchestrator.execute({
        "workflow": "new_feature",
        "params": request.dict()
    })
    
    return result
```

---

### C. 개발 환경 설정

```bash
# 1. 저장소 클론
git clone https://github.com/your-org/SynapseSimple.git
cd SynapseSimple

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일 편집:
# OPENAI_API_KEY=your-api-key
# ENVIRONMENT=development

# 5. 데이터베이스 초기화
python -m backend.db.init_db

# 6. 테스트 실행
pytest tests/

# 7. 서버 실행
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
streamlit run app.py --server.port 8501
```

---

### D. 테스트 예시

```python
# tests/test_agents/test_summary_agent.py

import pytest
from backend.agents.summary_agent import SummaryAgent

@pytest.fixture
def summary_agent():
    config = {
        "openai_api_key": "test-key",
        "cache_enabled": True
    }
    return SummaryAgent(config)

@pytest.mark.asyncio
async def test_direct_summarize(summary_agent):
    """짧은 문서 직접 요약 테스트"""
    
    task = {
        "task_type": "summarize_document",
        "session_id": "test-123",
        "summary_type": "balanced"
    }
    
    result = await summary_agent.execute(task)
    
    assert result['status'] == 'success'
    assert 'summary' in result
    assert len(result['summary']['tldr']) == 3
    assert result['summary']['quality_score'] >= 0.7

@pytest.mark.asyncio
async def test_map_reduce_summarize(summary_agent):
    """긴 문서 Map-Reduce 요약 테스트"""
    
    # 3000+ 토큰 문서 시뮬레이션
    task = {
        "task_type": "summarize_document",
        "session_id": "test-long-doc",
        "summary_type": "detailed"
    }
    
    result = await summary_agent.execute(task)
    
    assert result['status'] == 'success'
    assert result['processing_time'] < 15  # 15초 이내

def test_cache_hit(summary_agent):
    """캐시 히트 테스트"""
    
    # 첫 번째 호출
    result1 = summary_agent.execute(task)
    assert result1['cache_hit'] == False
    
    # 두 번째 호출 (캐시)
    result2 = summary_agent.execute(task)
    assert result2['cache_hit'] == True
    assert result2['processing_time'] < 0.5
```

---

### E. 배포 가이드

#### Docker 배포

```dockerfile
# Dockerfile

FROM python:3.10-slim

WORKDIR /app

# 시스템 패키지
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션
COPY . .

# 포트
EXPOSE 8000 8501

# 실행
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"]
```

```yaml
# docker-compose.yml

version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
  
  frontend:
    build: .
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8000
```

```bash
# 배포
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

---

## 17. 마무리

### 17.1 핵심 차별화 포인트

✅ **10개 전문 에이전트 시스템**
- 각 기능별 특화된 AI 에이전트
- 느슨한 결합, 높은 확장성
- 엔터프라이즈급 아키텍처

✅ **지능형 오케스트레이션**
- 에이전트 간 자동 조율
- 4개 주요 워크플로우
- 에러 처리 및 복구

✅ **완전한 학습 사이클**
- 진단 → 계획 → 실행 → 평가
- 개인화된 학습 경험
- 실시간 피드백

✅ **비용 효율적**
- 캐싱으로 90% 절감
- gpt-4o-mini 활용
- 사용자당 $0.021/월

---

### 17.2 학습 목표 달성

**학원 필수 요구사항**:
1. ✅ 문서 요약 (SummaryAgent)
2. ✅ Q&A (RAGAgent)
3. ✅ 문제 생성 (QuizAgent)
4. ✅ 자료 추천 (RecommendationAgent)

**추가 달성**:
5. ✅ 자동 채점 (GradingAgent)
6. ✅ 학습 진단 (DiagnosisAgent)
7. ✅ 학습 계획 (PlanningAgent)
8. ✅ 종합 평가 (EvaluationAgent)
9. ✅ 대화 관리 (ConversationAgent)
10. ✅ 시스템 조율 (OrchestratorAgent)

---

### 17.3 포트폴리오 강점

**기술적 깊이**:
- 멀티 에이전트 시스템 설계 경험
- RAG 파이프라인 구현
- LLM API 최적화 (캐싱, 토큰 관리)
- 벡터 데이터베이스 활용

**시스템 설계**:
- 마이크로서비스 아키텍처
- 워크플로우 오케스트레이션
- 확장 가능한 구조
- 에러 처리 및 복구

**비즈니스 가치**:
- 실제 문제 해결 (교육 지원)
- 비용 효율적 구현
- 확장 가능한 로드맵
- 사용자 중심 UX

---

### 17.4 다음 단계

**즉시 시작**:
1. GitHub 저장소 생성
2. Day 1 개발 착수 (BaseAgent)
3. v1.0 코드 통합

**단기 목표 (2주)**:
- 10개 에이전트 완성
- 4개 워크플로우 구현
- MVP 시연 준비

**중기 목표 (1개월)**:
- v2.0 고급 기능 (AI 채점)
- 사용자 테스트
- 피드백 반영

**장기 목표 (3개월)**:
- v3.0 음성 인터페이스
- 멀티모달 확장
- 베타 서비스 런칭

---

## 18. 연락처 & 지원

**프로젝트 관리**:
- GitHub: [저장소 URL]
- 문서: [Notion/Confluence URL]
- 이슈 트래커: GitHub Issues

**개발 팀**:
- PM: [이름]
- Backend: [이름]
- Frontend: [이름]
- AI/ML: [이름]

**멘토링**:
- 학원 강사: [이름]
- 기술 자문: [이름]

---

## 📝 체크리스트

### 시작 전 확인사항
- [ ] OpenAI API 키 발급
- [ ] GitHub 저장소 생성
- [ ] 개발 환경 설정 완료
- [ ] 팀원 역할 분담

### 개발 중 확인사항
- [ ] BaseAgent 구현
- [ ] 10개 에이전트 완성
- [ ] OrchestratorAgent 워크플로우
- [ ] API 엔드포인트 (10개)
- [ ] Streamlit UI (6페이지)
- [ ] 단위 테스트 (80%+ 커버리지)
- [ ] E2E 테스트

### 완료 전 확인사항
- [ ] README.md 작성
- [ ] API 문서 (Swagger)
- [ ] 아키텍처 다이어그램
- [ ] 시연 시나리오 준비
- [ ] 발표 자료 완성

---

## 🎯 최종 정리

**SynapseSimple v2.0 기본 - 10개 에이전트 시스템**

이 계획서는 학원 필수 요구사항을 충족하면서도, 엔터프라이즈급 **멀티 에이전트 아키텍처**를 구현하는 완전한 로드맵입니다.

**핵심 가치**:
1. 🎯 **전문성**: 각 기능별 특화된 AI 에이전트
2. 🔄 **확장성**: 새로운 에이전트 추가 용이
3. 🤖 **지능형**: 에이전트 간 자동 조율
4. 💰 **효율성**: 비용 최적화 ($0.021/사용자)
5. 📚 **완성도**: 진단→계획→실행→평가 전 주기

**이 프로젝트로 얻는 것**:
- 고급 시스템 설계 경험
- LLM 실전 활용 능력
- 포트폴리오 차별화
- 취업 경쟁력 강화

---

**v2.0 기본 계획서 작성 완료!** ✅

**다음 단계**:
1. 이 계획서를 `PROJECT_ROADMAP_V2_BASIC.md`로 저장
2. VSCode Claude에게 파일 생성 요청
3. Day 1 개발 시작!

**필요한 것**:
```
VSCode Claude에게 전달:
"PROJECT_ROADMAP_V2_BASIC.md 파일을 생성해줘.
내용은 위의 전체 계획서야."
```

---

## 📊 문서 통계

- **총 페이지**: 약 50페이지
- **섹션**: 18개 주요 섹션
- **에이전트**: 10개 상세 명세
- **API**: 10개 엔드포인트
- **워크플로우**: 4개 주요 시나리오
- **코드 예시**: 20+ 개
- **다이어그램**: 2개

---

**이 계획서가 여러분의 성공적인 프로젝트를 위한 완벽한 가이드가 되길 바랍니다!** 🚀

궁금한 점이나 추가 설명이 필요하면 언제든 문의하세요! 💪