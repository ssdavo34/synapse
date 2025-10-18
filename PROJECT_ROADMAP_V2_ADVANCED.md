# 🚀 SynapseSimple v2.0 고급 - 확장 계획서

## 1. 프로젝트 개요

### 1.1 v2.0 기본 완료 가정

**완료된 기능** (PROJECT_ROADMAP_V2_BASIC.md 기준)
- ✅ 문서 즉시 요약 (Map-Reduce, 캐싱)
- ✅ RAG 기반 Q&A (출처 포함)
- ✅ 객관식 퀴즈 (5문항 고정)
- ✅ 자료 추천 (Wikipedia)
- ✅ 학습자 진단 (레벨 판정)
- ✅ 학습 계획 생성 (3단계)
- ✅ 대화 세션 요약

**기술 스택**
- FastAPI, OpenAI, ChromaDB, Streamlit
- SQLite, PyMuPDF, tiktoken
- 비용: $19/월 (100명)

### 1.2 v2.0 고급 목표

**프로 수준 학습 지원 시스템 구축**

🎯 **핵심 목표**
- 다양한 평가 방식 (4가지 퀴즈 유형)
- AI 기반 지능형 채점 (단답형/주관식)
- Perplexity 스타일 UX (답변 없음 처리)
- 학습 분석 & 최적화 (약점 진단, 오답 노트)
- 차세대 인터페이스 준비 (음성 기능 예고)

🎓 **교육적 가치**
- 개인화된 학습 경험
- 데이터 기반 학습 전략
- 지속적인 학습 개선

---

## 2. v2.0 기본 vs 고급 비교

| 기능 | v2.0 기본 | v2.0 고급 |
|------|-----------|-----------|
| **퀴즈 유형** | 객관식만 | 객관식/단답형/O/X/주관식 ⭐ |
| **문제 수** | 5개 고정 | 1-30개 설정 가능 |
| **난이도** | 자동 | 선택 가능 (쉬움/보통/어려움) |
| **유형 비율** | 고정 | 사용자 정의 가능 |
| **채점 방식** | 자동 (객관식) | AI 채점 (단답형/주관식) ⭐ |
| **채점 시간** | 즉시 | 단답형 2-3초, 주관식 5-10초 |
| **채점 피드백** | 정답/오답 | 상세 피드백 + 개선점 |
| **OCR** | PyMuPDF만 | PyMuPDF → Google Vision 자동 ⭐ |
| **OCR 품질** | 90-95% | 98-99% (fallback) |
| **RAG 답변없음** | 에러 메시지 | Perplexity 스타일 UX ⭐ |
| **추천 질문** | ❌ | LLM 기반 자동 생성 |
| **공식 소스** | ❌ | 신뢰 기관 추천 |
| **요약 유형** | 3가지 기본 | + 맞춤형 지시사항 |
| **학습 분석** | ❌ | 패턴 분석/약점 진단 ⭐ |
| **오답 관리** | ❌ | 오답 노트 자동 생성 ⭐ |
| **약점 퀴즈** | ❌ | 약점 집중 맞춤 퀴즈 ⭐ |
| **진도율** | ❌ | 시각화 대시보드 |
| **학습 추이** | ❌ | 차트 및 통계 |
| **비용 모니터링** | ❌ | 실시간 추적 + 최적화 제안 |
| **UI/UX** | 기본 | 고급 시각화 + 인터랙션 |

**v2.0 고급 = 프로 수준 학습 플랫폼**

---

## 3. 핵심 확장 기능

### 3.1 🎯 다양한 퀴즈 유형 (Tier 1 확장) ⭐⭐⭐

#### 사용자 설정 모델

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class QuizConfig(BaseModel):
    """퀴즈 설정"""

    num_questions: int = Field(
        default=10,
        ge=1,
        le=30,
        description="문제 수 (1-30개)"
    )

    question_types: List[str] = Field(
        default=["multiple_choice"],
        description="문제 유형 리스트"
    )

    difficulty: Optional[str] = Field(
        default="auto",
        description="난이도: auto|easy|medium|hard"
    )

    mix_ratio: Optional[Dict[str, float]] = Field(
        default=None,
        description="유형별 비율 (합 1.0)"
    )

    focus_concepts: Optional[List[str]] = Field(
        default=None,
        description="집중 개념 (선택)"
    )

    include_explanations: bool = Field(
        default=True,
        description="해설 포함 여부"
    )

# 사용 예시
config = QuizConfig(
    num_questions=15,
    question_types=["multiple_choice", "short_answer", "essay"],
    difficulty="medium",
    mix_ratio={
        "multiple_choice": 0.5,  # 7-8문항
        "short_answer": 0.3,      # 4-5문항
        "essay": 0.2              # 2-3문항
    }
)
```

---

#### 문제 유형 1: 객관식 (Multiple Choice) - 기존 유지

```json
{
  "type": "multiple_choice",
  "question": "토마토 씨앗 파종 적기는?",
  "options": ["3월", "4월", "5월", "6월"],
  "correct_answer": 1,
  "explanation": "4월이 최적기입니다. 지역별로 차이가 있으나 중부지방 기준 4월 중순이 적당합니다.",
  "difficulty": "easy",
  "concept": "토마토 파종"
}
```

**채점 로직**
```python
def grade_multiple_choice(question: dict, answer: int) -> dict:
    """객관식 자동 채점"""

    is_correct = (answer == question['correct_answer'])

    return {
        'score': 10 if is_correct else 0,
        'max_score': 10,
        'is_correct': is_correct,
        'correct_answer': question['options'][question['correct_answer']],
        'student_answer': question['options'][answer],
        'explanation': question['explanation']
    }
```

---

#### 문제 유형 2: 단답형 (Short Answer) ⭐ NEW

```json
{
  "type": "short_answer",
  "question": "토마토 재배 적정 온도는?",
  "correct_answers": [
    "20-25도",
    "20~25℃",
    "20도에서 25도 사이",
    "섭씨 20도에서 25도"
  ],
  "keywords": {
    "required": ["20", "25"],
    "optional": ["도", "℃", "온도", "섭씨"]
  },
  "scoring_guide": {
    "perfect_match": 10,
    "all_keywords": 8,
    "partial_keywords": 5,
    "semantic_match": 6
  },
  "explanation": "토마토는 20-25℃가 최적 생육 온도입니다. 너무 낮으면 생육이 느리고, 너무 높으면 착과율이 떨어집니다.",
  "difficulty": "medium",
  "concept": "재배 환경"
}
```

**채점 로직 (하이브리드)**

```python
class ShortAnswerGrader:
    """단답형 채점 엔진"""

    def grade(self, question: dict, answer: str) -> dict:
        """2단계 하이브리드 채점"""

        # 전처리
        answer = self._preprocess(answer)

        # 1단계: 키워드 매칭 (빠름, 무료)
        keyword_result = self._keyword_matching(question, answer)

        # 신뢰도 높으면 바로 반환
        if keyword_result['confidence'] >= 0.8:
            logger.info(f"✅ 키워드 매칭 성공 (신뢰도: {keyword_result['confidence']})")
            return keyword_result

        # 2단계: AI 평가 (정확, 유료)
        logger.info("🤖 AI 평가 시작...")
        ai_result = self._ai_evaluation(question, answer)

        return ai_result

    def _keyword_matching(self, question: dict, answer: str) -> dict:
        """키워드 기반 채점"""

        keywords = question['keywords']
        scoring_guide = question['scoring_guide']

        # 정답 리스트 exact 매칭
        for correct_ans in question['correct_answers']:
            if self._fuzzy_match(answer, correct_ans):
                return {
                    'score': scoring_guide['perfect_match'],
                    'max_score': 10,
                    'method': 'exact_match',
                    'confidence': 1.0,
                    'matched_keywords': keywords['required'] + keywords['optional'],
                    'feedback': '✅ 정답입니다!'
                }

        # 필수 키워드 체크
        required_found = [kw for kw in keywords['required'] if kw in answer]
        optional_found = [kw for kw in keywords['optional'] if kw in answer]

        if len(required_found) == len(keywords['required']):
            # 필수 키워드 모두 포함
            score = scoring_guide['all_keywords']
            confidence = 0.85

        elif len(required_found) > 0:
            # 일부 키워드 포함
            score = scoring_guide['partial_keywords']
            confidence = 0.5

        else:
            # 키워드 없음 → AI 평가 필요
            return {
                'score': 0,
                'confidence': 0.0,
                'method': 'keyword_fail'
            }

        return {
            'score': score,
            'max_score': 10,
            'method': 'keyword_match',
            'confidence': confidence,
            'matched_keywords': required_found + optional_found,
            'missing_keywords': [kw for kw in keywords['required'] if kw not in required_found],
            'feedback': self._generate_keyword_feedback(required_found, keywords)
        }

    def _ai_evaluation(self, question: dict, answer: str) -> dict:
        """AI 기반 채점 (GPT-4o-mini)"""

        prompt = f"""당신은 교육 평가 전문가입니다.
학생의 단답형 답안을 채점하세요.

문제: {question['question']}

정답 예시:
{chr(10).join(['- ' + ans for ans in question['correct_answers']])}

필수 키워드: {', '.join(question['keywords']['required'])}
선택 키워드: {', '.join(question['keywords']['optional'])}

학생 답변: "{answer}"

다음 기준으로 채점 (0-10점):
- 정확성 (5점): 핵심 내용이 맞는가?
- 완전성 (3점): 필수 정보를 모두 포함했는가?
- 표현력 (2점): 명확하고 이해하기 쉬운가?

JSON 형식으로만 반환:
{{
  "score": 7,
  "accuracy_score": 4,
  "completeness_score": 2,
  "clarity_score": 1,
  "matched_keywords": ["20", "25"],
  "missing_keywords": ["온도"],
  "feedback": "핵심 내용은 맞지만 단위 표기가 부족합니다. '온도'라는 표현을 추가하면 더 좋습니다."
}}"""

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return {
            'score': result['score'],
            'max_score': 10,
            'method': 'ai_evaluation',
            'confidence': 0.95,
            'matched_keywords': result['matched_keywords'],
            'missing_keywords': result['missing_keywords'],
            'feedback': result['feedback'],
            'details': {
                'accuracy': result['accuracy_score'],
                'completeness': result['completeness_score'],
                'clarity': result['clarity_score']
            }
        }

    def _fuzzy_match(self, answer: str, correct: str, threshold: float = 0.9) -> bool:
        """퍼지 매칭 (Levenshtein 거리)"""

        from difflib import SequenceMatcher

        ratio = SequenceMatcher(None, answer.lower(), correct.lower()).ratio()
        return ratio >= threshold

    def _preprocess(self, text: str) -> str:
        """전처리"""

        # 공백 정리
        text = ' '.join(text.split())

        # 특수문자 제거 (선택적)
        # text = re.sub(r'[^\w\s가-힣]', '', text)

        return text.strip()
```

**UI 표시**

```python
# Streamlit UI
if result['method'] == 'exact_match':
    st.success(f"✅ 정답! ({result['score']}/10점)")
    st.write(result['feedback'])

elif result['method'] == 'keyword_match':
    st.info(f"⭕ 부분 정답 ({result['score']}/10점)")
    st.write(f"**매칭된 키워드:** {', '.join(result['matched_keywords'])}")
    if result['missing_keywords']:
        st.write(f"**누락된 키워드:** {', '.join(result['missing_keywords'])}")
    st.write(result['feedback'])

elif result['method'] == 'ai_evaluation':
    score_emoji = "✅" if result['score'] >= 7 else "⭕" if result['score'] >= 5 else "❌"
    st.write(f"{score_emoji} AI 채점: {result['score']}/10점")

    with st.expander("상세 평가"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("정확성", f"{result['details']['accuracy']}/5")
        with col2:
            st.metric("완전성", f"{result['details']['completeness']}/3")
        with col3:
            st.metric("표현력", f"{result['details']['clarity']}/2")

    st.write(f"**피드백:** {result['feedback']}")
```

---

#### 문제 유형 3: O/X (True/False) ⭐ NEW

```json
{
  "type": "true_false",
  "question": "토마토는 고온다습한 환경을 선호한다",
  "correct_answer": false,
  "explanation": "❌ 잘못된 설명입니다.\n\n토마토는 **고온건조**한 환경을 선호합니다. 고온다습하면 병해가 발생하기 쉽고, 특히 흰가루병이나 역병이 생길 수 있습니다.\n\n✅ 올바른 재배 환경:\n- 온도: 20-25℃\n- 습도: 60-70% (적정)\n- 통풍: 필수",
  "difficulty": "easy",
  "concept": "재배 환경",
  "common_mistake": "다습 환경을 선호한다고 오해하는 경우가 많음"
}
```

**채점 로직**

```python
def grade_true_false(question: dict, answer: bool) -> dict:
    """O/X 자동 채점"""

    is_correct = (answer == question['correct_answer'])

    return {
        'score': 10 if is_correct else 0,
        'max_score': 10,
        'is_correct': is_correct,
        'correct_answer': "⭕ 참 (True)" if question['correct_answer'] else "❌ 거짓 (False)",
        'student_answer': "⭕ 참 (True)" if answer else "❌ 거짓 (False)",
        'explanation': question['explanation'],
        'common_mistake': question.get('common_mistake')
    }
```

**UI**

```python
# Streamlit
st.write(f"**문제 {idx+1}.** {question['question']}")

col1, col2 = st.columns(2)

with col1:
    if st.button("⭕ 참 (True)", key=f"true_{idx}", use_container_width=True):
        answer = True
        submit_answer(idx, answer)

with col2:
    if st.button("❌ 거짓 (False)", key=f"false_{idx}", use_container_width=True):
        answer = False
        submit_answer(idx, answer)
```

---

#### 문제 유형 4: 주관식 (Essay) ⭐⭐ NEW

```json
{
  "type": "essay",
  "question": "토마토 병충해 관리 방법을 3가지 이상 서술하시오 (200-500자)",
  "min_length": 200,
  "max_length": 500,
  "evaluation_criteria": [
    {
      "name": "병충해 종류 언급",
      "points": 3,
      "description": "구체적인 병충해 이름 제시"
    },
    {
      "name": "예방 방법 설명",
      "points": 3,
      "description": "예방법을 명확히 기술"
    },
    {
      "name": "구체적 사례 제시",
      "points": 2,
      "description": "실제 적용 가능한 사례"
    },
    {
      "name": "논리적 서술",
      "points": 2,
      "description": "체계적이고 이해하기 쉬운 구성"
    }
  ],
  "rubric": {
    "excellent": {
      "range": "9-10점",
      "description": "3가지 이상 구체적 설명, 논리적 구성"
    },
    "good": {
      "range": "7-8점",
      "description": "2가지 명확한 설명, 적절한 구성"
    },
    "fair": {
      "range": "5-6점",
      "description": "1-2가지 기본 설명, 구성 부족"
    },
    "poor": {
      "range": "0-4점",
      "description": "부정확하거나 불충분한 내용"
    }
  },
  "sample_answer": "토마토 병충해 관리의 핵심은 예방입니다.\n\n1. **흰가루병 예방**: 통풍을 잘 유지하고 적정 습도(60-70%)를 유지합니다. 잎이 너무 밀집되지 않도록 적심과 곁순 제거를 합니다.\n\n2. **역병 관리**: 배수를 개선하고 물이 고이지 않도록 합니다. 감염된 잎은 즉시 제거하여 확산을 막습니다.\n\n3. **진딧물 방제**: 천적(무당벌레 등)을 이용하거나 친환경 약제를 사용합니다. 초기 발견이 중요하므로 정기적으로 잎 뒷면을 점검합니다.",
  "explanation": "병충해 관리는 예방이 80%입니다. 정기적인 점검과 적절한 환경 관리가 가장 중요합니다.",
  "difficulty": "hard",
  "concept": "병충해 관리"
}
```

**채점 로직 (AI 전용 - GPT-4)**

```python
class EssayGrader:
    """주관식 채점 엔진"""

    def grade(self, question: dict, answer: str) -> dict:
        """AI 기반 주관식 채점"""

        # 1. 길이 검증
        answer_length = len(answer.strip())

        if answer_length < question['min_length']:
            return {
                'score': 0,
                'max_score': 10,
                'grade': 'insufficient',
                'feedback': f"답변이 너무 짧습니다. ({answer_length}자 < {question['min_length']}자)\n최소 {question['min_length']}자 이상 작성해주세요."
            }

        if answer_length > question['max_length']:
            return {
                'score': 0,
                'max_score': 10,
                'grade': 'excessive',
                'feedback': f"답변이 너무 깁니다. ({answer_length}자 > {question['max_length']}자)\n최대 {question['max_length']}자 이내로 작성해주세요."
            }

        # 2. GPT-4 평가
        return self._ai_essay_evaluation(question, answer)

    def _ai_essay_evaluation(self, question: dict, answer: str) -> dict:
        """GPT-4 기반 주관식 평가"""

        # 평가 기준 포맷팅
        criteria_text = "\n".join([
            f"- {c['name']} ({c['points']}점): {c['description']}"
            for c in question['evaluation_criteria']
        ])

        # 루브릭 포맷팅
        rubric_text = "\n".join([
            f"- {level.upper()}: {info['range']} - {info['description']}"
            for level, info in question['rubric'].items()
        ])

        prompt = f"""당신은 농업 교육 전문가입니다.
학생의 주관식 답안을 엄격하게 채점하세요.

## 문제
{question['question']}

## 평가 기준 (총 10점)
{criteria_text}

## 채점 루브릭
{rubric_text}

## 모범 답안
{question['sample_answer']}

## 학생 답변
{answer}

## 채점 지침
1. 각 평가 기준별로 점수 부여
2. 모범 답안과 비교하여 정확성 평가
3. 구체성, 논리성, 완성도 고려
4. 강점과 개선점을 명확히 제시

JSON 형식으로만 반환:
{{
  "total_score": 8,
  "criteria_scores": {{
    "병충해 종류 언급": 3,
    "예방 방법 설명": 3,
    "구체적 사례 제시": 1,
    "논리적 서술": 1
  }},
  "strengths": [
    "3가지 병충해를 정확히 언급함",
    "예방 방법이 구체적이고 실용적임"
  ],
  "improvements": [
    "실제 적용 사례를 더 추가하면 좋겠음",
    "문장 간 논리적 연결이 약함"
  ],
  "feedback": "병충해 종류와 예방법은 잘 설명했습니다. 실제 농장에서 적용한 사례나 경험을 더 추가하면 설득력이 높아집니다. 또한 각 방법 간의 연관성을 설명하면 더욱 체계적인 답변이 될 것입니다.",
  "grade": "good"
}}"""

        response = openai.ChatCompletion.create(
            model="gpt-4o",  # 정확도 우선
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return {
            'score': result['total_score'],
            'max_score': 10,
            'method': 'ai_essay',
            'criteria_scores': result['criteria_scores'],
            'strengths': result['strengths'],
            'improvements': result['improvements'],
            'feedback': result['feedback'],
            'grade': result['grade'],
            'grade_label': question['rubric'][result['grade']]['description']
        }
```

**UI 표시 (상세 피드백)**

```python
# Streamlit 주관식 채점 결과
st.subheader(f"📝 주관식 채점 결과 ({result['score']}/10점)")

# 등급 배지
grade_colors = {
    'excellent': '🟢',
    'good': '🔵',
    'fair': '🟡',
    'poor': '🔴'
}

grade_emoji = grade_colors.get(result['grade'], '⚪')
st.write(f"{grade_emoji} **등급:** {result['grade'].upper()} - {result['grade_label']}")

st.divider()

# 평가 기준별 점수
st.write("**📊 평가 기준별 점수:**")

for criterion, score in result['criteria_scores'].items():
    # 해당 기준의 만점 찾기
    max_points = next(
        c['points'] for c in question['evaluation_criteria']
        if c['name'] == criterion
    )

    progress_value = score / max_points

    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.write(f"**{criterion}**")
        st.progress(progress_value)
    with col2:
        st.metric("점수", f"{score}/{max_points}")

st.divider()

# 강점
st.write("**✨ 강점:**")
for strength in result['strengths']:
    st.success(f"• {strength}")

st.divider()

# 개선점
st.write("**💡 개선점:**")
for improvement in result['improvements']:
    st.warning(f"• {improvement}")

st.divider()

# 종합 피드백
st.write("**📝 종합 피드백:**")
st.info(result['feedback'])

# 모범 답안 (선택적 표시)
with st.expander("📖 모범 답안 보기"):
    st.write(question['sample_answer'])
    st.caption(f"💡 {question['explanation']}")
```

---

#### 복합형 퀴즈 생성 예시

```python
# API 호출
config = {
    "num_questions": 15,
    "question_types": ["multiple_choice", "short_answer", "true_false", "essay"],
    "mix_ratio": {
        "multiple_choice": 0.4,   # 6문항
        "short_answer": 0.3,       # 4-5문항
        "true_false": 0.2,         # 3문항
        "essay": 0.1               # 1-2문항
    },
    "difficulty": "medium"
}

response = api_client.post("/api/diagnosis/generate", json=config)

# 응답
{
  "quiz_id": "uuid",
  "questions": [
    {...},  # 객관식 6개
    {...},  # 단답형 5개
    {...},  # O/X 3개
    {...}   # 주관식 1개
  ],
  "total_questions": 15,
  "estimated_time_minutes": 25,
  "difficulty_distribution": {
    "easy": 5,
    "medium": 7,
    "hard": 3
  }
}
```

**채점 시간 예상**

```python
# 15문항 복합형 퀴즈 채점 시간
채점_시간 = {
    '객관식 6문항': 0,           # 즉시
    'O/X 3문항': 0,              # 즉시
    '단답형 5문항': 5 * 2,       # 10초 (키워드 우선, 일부 AI)
    '주관식 1문항': 1 * 8        # 8초 (AI 전용)
}

총_채점_시간 = 18초  # 약 20초
```

---

### 3.2 📸 스마트 OCR 시스템 (Tier 1 확장) ⭐⭐

#### 2단계 OCR 전략

**목표**: 비용 최소화 + 정확도 극대화

```
┌─────────────┐
│ PDF 업로드  │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│ Step 1: PyMuPDF 시도 │  ← 1순위 (무료, 빠름)
└──────┬───────────────┘
       │
       ▼
┌──────────────────┐
│   품질 검증      │
└──────┬───────────┘
       │
       ├─ ✅ 양호 ─────────────► [사용] (90% 케이스)
       │                         비용: $0
       │                         시간: <1초
       │
       └─ ❌ 불량
           │
           ▼
       ┌────────────────────────────┐
       │ Step 2: Google Vision 시도 │  ← 2순위 (유료, 정확)
       └────────────┬───────────────┘
                    │
                    ▼
                [사용] (10% 케이스)
                비용: $0.0015/페이지
                시간: 3-5초
                정확도: 98-99%
```

#### 구현

```python
from google.cloud import vision
import fitz  # PyMuPDF
import re
from typing import Dict, Tuple

class SmartOCRService:
    """지능형 OCR 서비스"""

    def __init__(self):
        self.vision_client = vision.ImageAnnotatorClient()
        self.stats = {
            'pymupdf_success': 0,
            'google_vision_used': 0,
            'total_cost': 0.0
        }

    def extract_text(self, pdf_path: str) -> Dict:
        """2단계 OCR 파이프라인"""

        logger.info("=" * 60)
        logger.info(f"📄 OCR 시작: {pdf_path}")
        logger.info("=" * 60)

        # Step 1: PyMuPDF 시도
        logger.info("🔍 Step 1: PyMuPDF 추출 시도...")

        try:
            result_pymupdf = self._extract_with_pymupdf(pdf_path)

            # 품질 검증
            quality = self._validate_text_quality(result_pymupdf['text'])

            if quality['is_valid']:
                logger.info(f"✅ PyMuPDF 성공 (품질: {quality['score']:.2f})")

                self.stats['pymupdf_success'] += 1

                return {
                    'text': result_pymupdf['text'],
                    'method': 'pymupdf',
                    'cost': 0,
                    'time_seconds': result_pymupdf['time'],
                    'quality_score': quality['score'],
                    'page_count': result_pymupdf['page_count']
                }

            else:
                logger.warning(f"⚠️ PyMuPDF 품질 불량 (점수: {quality['score']:.2f})")
                logger.warning(f"   이유: {', '.join(quality['issues'])}")

        except Exception as e:
            logger.error(f"❌ PyMuPDF 실패: {str(e)}")

        # Step 2: Google Vision OCR
        logger.info("🔍 Step 2: Google Cloud Vision OCR 시도...")

        try:
            result_vision = self._extract_with_google_vision(pdf_path)

            logger.info(f"✅ Google Vision 성공")

            cost = self._calculate_vision_cost(result_vision['page_count'])
            self.stats['google_vision_used'] += 1
            self.stats['total_cost'] += cost

            return {
                'text': result_vision['text'],
                'method': 'google_vision',
                'cost': cost,
                'time_seconds': result_vision['time'],
                'quality_score': 0.98,  # Google Vision은 고품질
                'page_count': result_vision['page_count']
            }

        except Exception as e:
            logger.error(f"❌ Google Vision 실패: {str(e)}")
            raise OCRError("모든 OCR 방법 실패")

    def _extract_with_pymupdf(self, pdf_path: str) -> Dict:
        """PyMuPDF로 텍스트 추출"""

        import time
        start_time = time.time()

        doc = fitz.open(pdf_path)
        text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            text += page.get_text()

        doc.close()

        return {
            'text': text,
            'page_count': len(doc),
            'time': time.time() - start_time
        }

    def _validate_text_quality(self, text: str) -> Dict:
        """텍스트 품질 검증"""

        issues = []
        score = 1.0

        # 1. 최소 길이 확인
        if len(text) < 100:
            issues.append("텍스트 너무 짧음 (< 100자)")
            score -= 0.5

        # 2. 문자 비율 확인
        korean_chars = len([c for c in text if '가' <= c <= '힣'])
        english_chars = len([c for c in text if c.isalpha() and not ('가' <= c <= '힣')])
        numeric_chars = len([c for c in text if c.isdigit()])

        total_meaningful = korean_chars + english_chars + numeric_chars

        if total_meaningful < len(text) * 0.6:
            issues.append(f"의미 있는 문자 비율 낮음 ({total_meaningful}/{len(text)} = {total_meaningful/len(text):.1%})")
            score -= 0.3

        # 3. 특수문자 과다 확인
        special_chars = len([c for c in text if not c.isalnum() and c not in ' \n\t'])

        if special_chars / len(text) > 0.4:
            issues.append(f"특수문자 과다 ({special_chars/len(text):.1%})")
            score -= 0.2

        # 4. 반복 문자 패턴 확인 (OCR 실패 징후)
        repeat_pattern = re.findall(r'(.)\1{5,}', text)
        if repeat_pattern:
            issues.append(f"반복 문자 패턴 발견: {len(repeat_pattern)}개")
            score -= 0.1

        # 5. 문장 구조 확인
        sentences = text.split('.')
        if len(sentences) < 3:
            issues.append("문장 구조 부족")
            score -= 0.1

        is_valid = score >= 0.7

        return {
            'is_valid': is_valid,
            'score': max(0, score),
            'issues': issues,
            'stats': {
                'total_chars': len(text),
                'korean_chars': korean_chars,
                'english_chars': english_chars,
                'special_chars': special_chars
            }
        }

    def _extract_with_google_vision(self, pdf_path: str) -> Dict:
        """Google Cloud Vision으로 텍스트 추출"""

        import time
        start_time = time.time()

        # PDF를 이미지로 변환
        doc = fitz.open(pdf_path)
        all_text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]

            # 페이지를 이미지로 렌더링
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2배 해상도
            img_bytes = pix.tobytes("png")

            # Google Vision API 호출
            image = vision.Image(content=img_bytes)
            response = self.vision_client.text_detection(image=image)

            if response.text_annotations:
                page_text = response.text_annotations[0].description
                all_text += page_text + "\n\n"

            # API 속도 제한 고려
            time.sleep(0.1)

        doc.close()

        return {
            'text': all_text,
            'page_count': len(doc),
            'time': time.time() - start_time
        }

    def _calculate_vision_cost(self, page_count: int) -> float:
        """Google Vision 비용 계산"""

        # Google Vision 가격: $1.50 per 1000 pages
        # 첫 1000 pages/month 무료

        cost_per_page = 0.0015
        return page_count * cost_per_page

    def get_stats(self) -> Dict:
        """OCR 통계"""

        total = self.stats['pymupdf_success'] + self.stats['google_vision_used']

        return {
            'total_extractions': total,
            'pymupdf_success': self.stats['pymupdf_success'],
            'pymupdf_rate': self.stats['pymupdf_success'] / total if total > 0 else 0,
            'google_vision_used': self.stats['google_vision_used'],
            'google_vision_rate': self.stats['google_vision_used'] / total if total > 0 else 0,
            'total_cost': self.stats['total_cost'],
            'avg_cost_per_extraction': self.stats['total_cost'] / total if total > 0 else 0
        }
```

#### 비용 절감 효과

```python
# 시나리오: 100개 PDF 파일 (평균 10페이지)

# Google Vision만 사용 시
google_only_cost = 100 * 10 * 0.0015 = $1.50

# 스마트 OCR 전략 (PyMuPDF 90% 성공)
smart_ocr_cost = (
    90 * 0 +           # PyMuPDF 성공: $0
    10 * 10 * 0.0015   # Google Vision: $0.15
) = $0.15

# 절감율
savings = (1.50 - 0.15) / 1.50 = 90%

print(f"💰 비용 절감: ${1.50 - 0.15:.2f} (90%)")
```

---

### 3.3 🔍 Perplexity 스타일 답변 없음 처리 (Tier 1 확장) ⭐⭐

#### 목표
- 유사도 < 0.7 또는 검색 실패 시 사용자 친화적 응답
- Perplexity처럼 대안 제시

#### 응답 구조

```python
from pydantic import BaseModel
from typing import List, Optional

class NoAnswerResponse(BaseModel):
    """답변 없음 응답"""

    answer: None = None
    status: str = "no_answer"
    message: str = "📭 현재 보유 자료에는 문의하신 내용이 없습니다"

    # 1. 추천 질문 (LLM 생성)
    suggested_questions: List[str]

    # 2. 질문 개선 팁
    question_improvement_tips: List[str]

    # 3. 공식 출처 추천
    official_sources: List[dict]

    # 4. 웹 검색 키워드
    web_search_keywords: List[str]

    # 5. 대체 행동
    alternative_actions: List[dict]

# 예시
{
  "answer": null,
  "status": "no_answer",
  "message": "📭 현재 보유 자료에는 문의하신 내용이 없습니다",

  "suggested_questions": [
    "토마토 씨앗 파종 시기는?",
    "토마토 물주기 주기는?",
    "토마토 지주대 설치 방법은?"
  ],

  "question_improvement_tips": [
    "💡 더 구체적인 키워드를 사용해보세요",
    "💡 증상이나 상황을 추가해보세요",
    "💡 예: '토마토 잎이 노랗게 변하는 이유는?'"
  ],

  "official_sources": [
    {
      "name": "농촌진흥청",
      "url": "https://www.rda.go.kr",
      "trust_level": "high",
      "description": "정부 공식 농업 정보"
    },
    {
      "name": "농사로",
      "url": "https://www.nongsaro.go.kr",
      "trust_level": "high",
      "description": "농업기술 종합 정보"
    }
  ],

  "web_search_keywords": ["토마토", "재배", "관리"],

  "alternative_actions": [
    {
      "type": "upload_document",
      "label": "📄 다른 학습 자료 업로드",
      "description": "관련 PDF를 추가로 업로드하세요",
      "action": "redirect_to_upload"
    },
    {
      "type": "web_search",
      "label": "🔍 웹에서 검색",
      "links": {
        "google": "https://www.google.com/search?q=토마토+재배+관리",
        "naver": "https://search.naver.com/search.naver?query=토마토+재배"
      }
    },
    {
      "type": "official_site",
      "label": "🏛️ 공식 사이트 방문",
      "description": "신뢰할 수 있는 정보원 확인"
    },
    {
      "type": "wikipedia",
      "label": "📖 Wikipedia 검색",
      "description": "관련 백과사전 정보"
    }
  ]
}
```

#### 구현

```python
class PerplexityStyleHandler:
    """Perplexity 스타일 답변없음 처리"""

    def handle_no_answer(
        self,
        question: str,
        search_results: list,
        threshold: float = 0.7
    ) -> dict:
        """답변 없음 시 대응"""

        # 유사도 체크
        has_relevant = any(r['similarity'] >= threshold for r in search_results)

        if has_relevant:
            # 정상 답변
            return self._generate_normal_answer(question, search_results)

        # 답변 없음 처리
        logger.info(f"📭 답변 없음: {question}")

        return {
            'answer': None,
            'status': 'no_answer',
            'message': '📭 현재 보유 자료에는 문의하신 내용이 없습니다',
            'suggested_questions': self._generate_suggested_questions(question),
            'question_improvement_tips': self._get_improvement_tips(),
            'official_sources': self._get_official_sources(question),
            'web_search_keywords': self._extract_keywords(question),
            'alternative_actions': self._get_alternative_actions(question)
        }

    def _generate_suggested_questions(self, question: str) -> List[str]:
        """LLM으로 추천 질문 생성"""

        prompt = f"""사용자 질문: "{question}"

이 질문과 관련된 추천 질문 3개를 생성하세요:
1. 더 구체적인 질문
2. 다른 각도의 질문
3. 관련된 기초 질문

예시:
사용자 질문: "토마토 재배"
추천 질문:
1. "토마토 씨앗 파종 시기는 언제인가요?"
2. "토마토 물주기 주기는 어떻게 되나요?"
3. "토마토 재배 시 필요한 도구는 무엇인가요?"

JSON 배열로만 반환: ["질문1", "질문2", "질문3"]"""

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result.get('questions', [])

    def _get_improvement_tips(self) -> List[str]:
        """질문 개선 팁"""

        return [
            "💡 더 구체적인 키워드를 사용해보세요 (예: '병충해' → '흰가루병')",
            "💡 증상이나 상황을 추가해보세요 (예: '잎이 노랗게 변함')",
            "💡 '어떻게', '왜', '무엇을' 등을 포함해보세요",
            "💡 문맥을 더 상세히 설명해보세요"
        ]

    def _get_official_sources(self, question: str) -> List[dict]:
        """공식 출처 추천"""

        # 도메인별 공식 소스 매핑
        sources_db = {
            '농업': [
                {
                    'name': '농촌진흥청',
                    'url': 'https://www.rda.go.kr',
                    'trust_level': 'high',
                    'description': '정부 공식 농업 연구 기관'
                },
                {
                    'name': '농사로',
                    'url': 'https://www.nongsaro.go.kr',
                    'trust_level': 'high',
                    'description': '농업기술 종합 정보 시스템'
                }
            ],
            '교육': [
                {
                    'name': '한국교육학술정보원',
                    'url': 'https://www.keris.or.kr',
                    'trust_level': 'high',
                    'description': '교육 정보 공식 기관'
                }
            ]
        }

        # 질문 도메인 감지 (간단한 키워드 매칭)
        for domain, sources in sources_db.items():
            if any(keyword in question for keyword in self._get_domain_keywords(domain)):
                return sources

        # 기본 공식 소스
        return [
            {
                'name': 'Wikipedia',
                'url': 'https://ko.wikipedia.org',
                'trust_level': 'medium',
                'description': '백과사전 정보'
            }
        ]

    def _extract_keywords(self, question: str) -> List[str]:
        """질문에서 키워드 추출"""

        # 간단한 키워드 추출 (형태소 분석 생략)
        keywords = []

        # 명사 추출 (간단한 방법)
        import re
        words = re.findall(r'[가-힣]+', question)

        # 2글자 이상 단어만
        keywords = [w for w in words if len(w) >= 2]

        return keywords[:5]  # 최대 5개

    def _get_alternative_actions(self, question: str) -> List[dict]:
        """대체 행동 제안"""

        keywords = '+'.join(self._extract_keywords(question))

        return [
            {
                'type': 'upload_document',
                'label': '📄 다른 학습 자료 업로드',
                'description': '관련 PDF를 추가로 업로드하세요',
                'action': 'redirect_to_upload'
            },
            {
                'type': 'web_search',
                'label': '🔍 웹에서 검색',
                'links': {
                    'google': f'https://www.google.com/search?q={keywords}',
                    'naver': f'https://search.naver.com/search.naver?query={keywords}',
                    'bing': f'https://www.bing.com/search?q={keywords}'
                }
            },
            {
                'type': 'official_site',
                'label': '🏛️ 공식 사이트 방문',
                'description': '신뢰할 수 있는 정보원 확인'
            },
            {
                'type': 'wikipedia',
                'label': '📖 Wikipedia 검색',
                'description': '관련 백과사전 정보',
                'url': f'https://ko.wikipedia.org/wiki/Special:Search?search={keywords}'
            }
        ]
```

#### UI 구현 (Streamlit)

```python
# Q&A 페이지
if response['status'] == 'no_answer':

    # 메인 메시지
    st.warning("📭 **현재 보유 자료에는 문의하신 내용이 없습니다**")
    st.caption("다른 방법으로 정보를 찾아보세요!")

    st.markdown("---")

    # 1. 추천 질문
    st.subheader("🔄 이런 질문은 어떠세요?")
    st.caption("클릭하면 자동으로 질문됩니다")

    for idx, suggestion in enumerate(response['suggested_questions'], 1):
        col1, col2 = st.columns([0.85, 0.15])

        with col1:
            st.write(f"**{idx}.** {suggestion}")

        with col2:
            if st.button("🔍 질문", key=f"suggest_{idx}"):
                # 자동 재질문
                st.session_state.auto_question = suggestion
                st.rerun()

    st.markdown("---")

    # 2. 질문 개선 팁
    with st.expander("💡 **질문을 더 구체적으로 만드는 방법**", expanded=False):
        for tip in response['question_improvement_tips']:
            st.write(f"• {tip}")

        st.info("**예시:**\n- 모호한 질문: '토마토 관리'\n- 구체적 질문: '토마토 잎이 노랗게 변하는 이유는?'")

    st.markdown("---")

    # 3. 공식 출처 추천
    st.subheader("🏛️ 신뢰할 수 있는 정보원")

    for source in response['official_sources']:
        with st.container():
            col1, col2, col3 = st.columns([0.5, 0.3, 0.2])

            with col1:
                st.write(f"**{source['name']}**")
                st.caption(source['description'])

            with col2:
                if source['trust_level'] == 'high':
                    st.success("🟢 **공식**")
                else:
                    st.info("🟡 **검증됨**")

            with col3:
                st.link_button("방문 →", source['url'], use_container_width=True)

    st.markdown("---")

    # 4. 웹 검색 제안
    st.subheader("🔍 웹에서 검색해보세요")

    keywords = ' '.join(response['web_search_keywords'])
    st.write(f"**추천 검색어:** `{keywords}`")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.link_button(
            "🔍 Google",
            f"https://www.google.com/search?q={keywords}",
            use_container_width=True
        )

    with col2:
        st.link_button(
            "🔍 Naver",
            f"https://search.naver.com/search.naver?query={keywords}",
            use_container_width=True
        )

    with col3:
        st.link_button(
            "🔍 Bing",
            f"https://www.bing.com/search?q={keywords}",
            use_container_width=True
        )

    st.markdown("---")

    # 5. 대체 행동
    st.subheader("📚 다른 방법으로 학습하기")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📄 자료 추가", type="primary", use_container_width=True):
            st.switch_page("pages/1_Home.py")

    with col2:
        if st.button("📖 Wikipedia", use_container_width=True):
            st.switch_page("pages/6_Wikipedia.py")

    with col3:
        if st.button("❓ 질문 가이드", use_container_width=True):
            st.session_state.show_guide = True
            st.rerun()

    with col4:
        if st.button("🏠 홈으로", use_container_width=True):
            st.switch_page("pages/1_Home.py")
```

---

### 3.4 📊 학습 분석 & 최적화 (Tier 1 확장) ⭐⭐⭐

#### 3.4.1 학습 패턴 분석

```python
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime, timedelta

@dataclass
class LearningPattern:
    """학습 패턴"""

    total_study_time: int  # 분
    sessions_count: int
    avg_session_duration: int
    most_active_hour: int
    most_active_day: str
    study_streak: int  # 연속 일수

class LearningAnalyzer:
    """학습 패턴 분석기"""

    def __init__(self, db: StateDB):
        self.db = db

    def analyze_session(self, session_id: str) -> dict:
        """세션 종합 분석"""

        return {
            'quiz_performance': self._analyze_quiz_performance(session_id),
            'qa_patterns': self._analyze_qa_patterns(session_id),
            'time_investment': self._analyze_time_investment(session_id),
            'concept_mastery': self._analyze_concept_mastery(session_id),
            'weaknesses': self._identify_weaknesses(session_id),
            'strengths': self._identify_strengths(session_id),
            'recommendations': self._generate_recommendations(session_id)
        }

    def _analyze_quiz_performance(self, session_id: str) -> dict:
        """퀴즈 성과 분석"""

        quizzes = self.db.get_quizzes_by_session(session_id)

        if not quizzes:
            return {'total_quizzes': 0}

        # 유형별 성과
        by_type = {}
        for quiz in quizzes:
            q_type = quiz['type']
            if q_type not in by_type:
                by_type[q_type] = {'total': 0, 'correct': 0, 'scores': []}

            by_type[q_type]['total'] += 1
            by_type[q_type]['scores'].append(quiz['score'])
            if quiz.get('is_correct', quiz['score'] >= 7):
                by_type[q_type]['correct'] += 1

        # 통계 계산
        for q_type, stats in by_type.items():
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
            stats['accuracy'] = stats['correct'] / stats['total']

        # 난이도별 성과
        by_difficulty = self._group_by_difficulty(quizzes)

        # 추이 분석
        trend = self._calculate_trend(quizzes)

        return {
            'total_quizzes': len(quizzes),
            'average_score': sum(q['score'] for q in quizzes) / len(quizzes),
            'by_type': by_type,
            'by_difficulty': by_difficulty,
            'improvement_trend': trend,
            'latest_score': quizzes[-1]['score'] if quizzes else 0
        }

    def _calculate_trend(self, quizzes: List[dict]) -> dict:
        """학습 추이 분석"""

        if len(quizzes) < 2:
            return {'trend': 'insufficient_data'}

        scores = [q['score'] for q in quizzes]

        # 선형 회귀 (간단한 방법)
        n = len(scores)
        x = list(range(n))

        # 기울기 계산
        x_mean = sum(x) / n
        y_mean = sum(scores) / n

        numerator = sum((x[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        slope = numerator / denominator if denominator != 0 else 0

        # 추세 판정
        if slope > 1:
            trend = 'improving'
            message = '📈 점수가 꾸준히 상승하고 있습니다!'
        elif slope > 0:
            trend = 'slightly_improving'
            message = '📊 점수가 조금씩 상승하고 있습니다'
        elif slope > -1:
            trend = 'stable'
            message = '➡️ 점수가 안정적입니다'
        else:
            trend = 'declining'
            message = '📉 점수가 하락 추세입니다. 복습이 필요합니다!'

        return {
            'trend': trend,
            'slope': slope,
            'message': message,
            'recent_avg': sum(scores[-3:]) / min(3, len(scores)),  # 최근 3개 평균
            'early_avg': sum(scores[:3]) / min(3, len(scores))      # 초기 3개 평균
        }

    def _identify_weaknesses(self, session_id: str) -> List[dict]:
        """약점 파악"""

        # 오답 분석
        wrong_answers = self.db.get_wrong_answers(session_id)

        # 개념별 그룹핑
        concept_errors = {}
        for wa in wrong_answers:
            concept = wa['concept']
            if concept not in concept_errors:
                concept_errors[concept] = []
            concept_errors[concept].append(wa)

        # 약점 순위
        weaknesses = []
        for concept, errors in concept_errors.items():
            weakness_score = self._calculate_weakness_score(errors)

            weaknesses.append({
                'concept': concept,
                'wrong_count': len(errors),
                'score': weakness_score,
                'avg_difficulty': sum(self._difficulty_to_num(e['difficulty']) for e in errors) / len(errors),
                'recent_wrong': len([e for e in errors if (datetime.now() - e['attempted_at']).days < 7]),
                'recommendation': self._get_weakness_recommendation(concept, errors)
            })

        # 점수 높은 순 (약점 우선)
        weaknesses.sort(key=lambda x: x['score'], reverse=True)

        return weaknesses[:5]  # 상위 5개

    def _calculate_weakness_score(self, errors: List[dict]) -> int:
        """약점 점수 계산 (높을수록 심각)"""

        score = 0

        # 1. 오답 횟수
        score += len(errors) * 10

        # 2. 최근 오답 가중치
        recent_errors = [e for e in errors if (datetime.now() - e['attempted_at']).days < 7]
        score += len(recent_errors) * 15

        # 3. 난이도 가중치
        for error in errors:
            if error['difficulty'] == 'hard':
                score += 5
            elif error['difficulty'] == 'medium':
                score += 3
            else:
                score += 1

        # 4. 반복 오답
        repeated_errors = len([e for e in errors if e.get('wrong_count', 1) > 1])
        score += repeated_errors * 20

        return score
```

#### 3.4.2 오답 노트 자동 생성 ⭐⭐

```python
class WrongAnswerNotebook:
    """오답 노트 관리"""

    def __init__(self, db: StateDB):
        self.db = db

    def generate_note(self, session_id: str) -> dict:
        """오답 노트 생성"""

        wrong_answers = self.db.get_wrong_answers(session_id)

        if not wrong_answers:
            return {
                'total_wrong': 0,
                'message': '🎉 오답이 없습니다!'
            }

        # 유형별 그룹핑
        grouped_by_type = {
            'multiple_choice': [],
            'short_answer': [],
            'true_false': [],
            'essay': []
        }

        for wa in wrong_answers:
            q_type = wa['type']
            if q_type in grouped_by_type:
                grouped_by_type[q_type].append(wa)

        # 개념별 분류
        grouped_by_concept = {}
        for wa in wrong_answers:
            concept = wa['concept']
            if concept not in grouped_by_concept:
                grouped_by_concept[concept] = []
            grouped_by_concept[concept].append(wa)

        # 복습 우선순위
        priorities = self._calculate_review_priority(wrong_answers)

        # 통계
        stats = {
            'total_wrong': len(wrong_answers),
            'by_type': {k: len(v) for k, v in grouped_by_type.items() if v},
            'by_concept_count': len(grouped_by_concept),
            'repeated_errors': len([wa for wa in wrong_answers if wa.get('wrong_count', 1) > 1]),
            'recent_errors_7days': len([wa for wa in wrong_answers if (datetime.now() - wa['attempted_at']).days < 7])
        }

        return {
            'total_wrong': len(wrong_answers),
            'stats': stats,
            'by_type': grouped_by_type,
            'by_concept': grouped_by_concept,
            'review_priority': priorities,
            'estimated_review_time_minutes': len(wrong_answers) * 5,
            'recommendations': self._generate_review_recommendations(priorities)
        }

    def _calculate_review_priority(self, wrong_answers: List[dict]) -> List[dict]:
        """복습 우선순위 계산"""

        priority_list = []

        for wa in wrong_answers:
            score = 0
            reasons = []

            # 1. 반복 오답 (가장 중요)
            wrong_count = wa.get('wrong_count', 1)
            if wrong_count > 1:
                score += wrong_count * 15
                reasons.append(f"🔴 {wrong_count}번 틀림 (반복 오답)")

            # 2. 최근 오답
            days_ago = (datetime.now() - wa['attempted_at']).days
            if days_ago < 3:
                score += 20
                reasons.append("🆕 최근 3일 이내 오답")
            elif days_ago < 7:
                score += 10
                reasons.append("📅 최근 1주일 이내 오답")

            # 3. 난이도
            difficulty_weights = {'easy': 5, 'medium': 10, 'hard': 15}
            diff_score = difficulty_weights.get(wa['difficulty'], 10)
            score += diff_score
            reasons.append(f"📊 난이도: {wa['difficulty']}")

            # 4. 핵심 개념 여부
            if wa.get('is_core_concept', False):
                score += 20
                reasons.append("⭐ 핵심 개념")

            # 5. 문제 유형 (주관식/에세이 우선)
            if wa['type'] == 'essay':
                score += 10
                reasons.append("✍️ 주관식 문제")
            elif wa['type'] == 'short_answer':
                score += 5
                reasons.append("📝 단답형 문제")

            priority_list.append({
                'question': wa,
                'priority_score': score,
                'reasons': reasons,
                'recommended_review_time': self._estimate_review_time(wa)
            })

        # 점수 높은 순 정렬
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)

        return priority_list

    def _estimate_review_time(self, wrong_answer: dict) -> int:
        """복습 예상 시간 (분)"""

        base_time = 5

        # 유형별 가중치
        if wrong_answer['type'] == 'essay':
            base_time += 10
        elif wrong_answer['type'] == 'short_answer':
            base_time += 3

        # 난이도별 가중치
        if wrong_answer['difficulty'] == 'hard':
            base_time += 5
        elif wrong_answer['difficulty'] == 'medium':
            base_time += 2

        return base_time

    def _generate_review_recommendations(self, priorities: List[dict]) -> List[str]:
        """복습 권장사항"""

        recommendations = []

        if not priorities:
            return ["🎉 오답이 없습니다! 복습이 필요하지 않습니다."]

        # 반복 오답 있으면
        repeated = [p for p in priorities if p['question'].get('wrong_count', 1) > 1]
        if repeated:
            recommendations.append(f"🔴 **반복 오답 {len(repeated)}개**: 우선적으로 복습하세요!")

        # 최근 오답 많으면
        recent = [p for p in priorities if (datetime.now() - p['question']['attempted_at']).days < 7]
        if len(recent) > 5:
            recommendations.append(f"📅 **최근 1주일 오답 {len(recent)}개**: 즉시 복습이 필요합니다")

        # 특정 개념 집중
        concepts = {}
        for p in priorities:
            concept = p['question']['concept']
            concepts[concept] = concepts.get(concept, 0) + 1

        if concepts:
            most_common = max(concepts.items(), key=lambda x: x[1])
            if most_common[1] >= 3:
                recommendations.append(f"⭐ **'{most_common[0]}' 개념**: {most_common[1]}번 틀림. 집중 학습 권장")

        # 총 복습 시간
        total_time = sum(p['recommended_review_time'] for p in priorities)
        recommendations.append(f"⏱️ **예상 복습 시간**: {total_time}분 ({total_time // 60}시간 {total_time % 60}분)")

        return recommendations
```

#### 3.4.3 약점 집중 퀴즈 생성 ⭐⭐

```python
class WeaknessTargetedQuizzer:
    """약점 집중 퀴즈 생성기"""

    def __init__(self, db: StateDB, vector_db, llm_client):
        self.db = db
        self.vector_db = vector_db
        self.llm = llm_client

    def generate_targeted_quiz(
        self,
        session_id: str,
        focus_concepts: List[str] = None,
        num_questions: int = 10
    ) -> dict:
        """약점 집중 맞춤 퀴즈 생성"""

        # 약점 자동 감지
        if not focus_concepts:
            analyzer = LearningAnalyzer(self.db)
            weaknesses = analyzer._identify_weaknesses(session_id)

            if not weaknesses:
                return {
                    'error': '약점이 감지되지 않았습니다',
                    'message': '🎉 모든 영역에서 우수한 성적을 보이고 있습니다!'
                }

            focus_concepts = [w['concept'] for w in weaknesses[:3]]

        logger.info(f"🎯 약점 집중 퀴즈 생성: {', '.join(focus_concepts)}")

        # 약점 개념 관련 청크 추출
        related_chunks = []
        for concept in focus_concepts:
            chunks = self.vector_db.search_by_metadata(
                session_id=session_id,
                filters={'concept': concept},
                top_k=5
            )
            related_chunks.extend(chunks)

        # 중복 제거
        unique_chunks = list({c['id']: c for c in related_chunks}.values())

        # 퀴즈 생성 프롬프트
        prompt = f"""당신은 교육 전문가입니다.
학생의 약점 개념을 집중적으로 보완하기 위한 퀴즈를 생성하세요.

## 약점 개념
{', '.join(focus_concepts)}

## 학습 자료
{self._format_chunks(unique_chunks)}

## 요구사항
- 문제 수: {num_questions}개
- 약점 개념을 집중적으로 다룰 것
- 난이도를 점진적으로 높일 것 (쉬움 → 보통 → 어려움)
- 실전 응용 문제 포함
- 다양한 문제 유형 혼합 (객관식, 단답형, 주관식)

## 목표
학생이 약점 개념을 확실히 이해하고 적용할 수 있도록 돕기

[JSON 형식으로 퀴즈 생성...]
"""

        # LLM 호출
        quiz = self.llm.generate_quiz(prompt)

        return {
            'quiz_id': str(uuid.uuid4()),
            'type': 'weakness_targeted',
            'focus_concepts': focus_concepts,
            'questions': quiz['questions'],
            'total_questions': len(quiz['questions']),
            'learning_goal': f"{', '.join(focus_concepts)} 개념 강화",
            'difficulty_progression': 'gradual',
            'estimated_time_minutes': len(quiz['questions']) * 3
        }

    def _format_chunks(self, chunks: List[dict]) -> str:
        """청크 포맷팅"""

        formatted = []
        for idx, chunk in enumerate(chunks, 1):
            formatted.append(f"[Chunk {idx}]\n{chunk['text']}\n")

        return '\n'.join(formatted)
```

---

### 3.5 💰 비용 모니터링 & 최적화 (Tier 1 확장)

```python
from collections import defaultdict
from datetime import datetime, timedelta

class AdvancedCostMonitor:
    """고급 비용 모니터링"""

    def __init__(self, db: StateDB):
        self.db = db

        # 비용 테이블
        self.costs = {
            'embedding': 0.0001,           # per 1K tokens
            'summary_short': 0.001,        # GPT-4o-mini (< 3K tokens)
            'summary_long': 0.005,         # GPT-4o-mini Map-Reduce
            'qa_answer': 0.002,            # GPT-4o-mini
            'quiz_generation': 0.003,      # GPT-4o-mini
            'short_answer_keyword': 0,     # 무료 (키워드 매칭)
            'short_answer_ai': 0.001,      # GPT-4o-mini (AI 평가)
            'essay_grading': 0.02,         # GPT-4o (정확도 우선)
            'similar_questions': 0.001,    # GPT-4o-mini
            'google_ocr': 0.0015           # per page
        }

    def track_operation(
        self,
        operation_type: str,
        session_id: str = None,
        tokens: dict = None,
        **kwargs
    ) -> float:
        """작업별 비용 추적"""

        cost = self._calculate_cost(operation_type, tokens, **kwargs)

        # 로그 저장
        self.db.log_cost({
            'timestamp': datetime.now(),
            'session_id': session_id,
            'operation': operation_type,
            'cost': cost,
            'tokens': tokens,
            'metadata': kwargs
        })

        logger.info(f"💰 {operation_type}: ${cost:.4f}")

        return cost

    def _calculate_cost(self, operation_type: str, tokens: dict = None, **kwargs) -> float:
        """비용 계산"""

        if operation_type not in self.costs:
            logger.warning(f"⚠️ Unknown operation: {operation_type}")
            return 0.0

        base_cost = self.costs[operation_type]

        # 토큰 기반 비용
        if tokens and operation_type != 'google_ocr':
            total_tokens = tokens.get('input', 0) + tokens.get('output', 0)
            return base_cost * (total_tokens / 1000)

        # Google OCR (페이지 기반)
        elif operation_type == 'google_ocr':
            pages = kwargs.get('pages', 1)
            return base_cost * pages

        # 고정 비용
        else:
            return base_cost

    def get_session_cost_breakdown(self, session_id: str) -> dict:
        """세션별 비용 분석"""

        logs = self.db.get_cost_logs(session_id)

        breakdown = {
            'total': 0.0,
            'by_operation': defaultdict(float),
            'timeline': [],
            'count_by_operation': defaultdict(int)
        }

        for log in logs:
            operation = log['operation']
            cost = log['cost']

            breakdown['total'] += cost
            breakdown['by_operation'][operation] += cost
            breakdown['count_by_operation'][operation] += 1
            breakdown['timeline'].append({
                'timestamp': log['timestamp'],
                'operation': operation,
                'cost': cost
            })

        return dict(breakdown)

    def suggest_optimizations(self, session_id: str) -> List[dict]:
        """비용 최적화 제안"""

        breakdown = self.get_session_cost_breakdown(session_id)
        suggestions = []

        # 1. 주관식 문제 과다
        essay_cost = breakdown['by_operation'].get('essay_grading', 0)
        essay_count = breakdown['count_by_operation'].get('essay_grading', 0)

        if essay_cost > 0.5 or essay_count > 10:
            suggestions.append({
                'type': 'warning',
                'severity': 'high',
                'message': f'주관식 문제 채점 비용이 높습니다 (${essay_cost:.2f}, {essay_count}회)',
                'recommendation': '객관식/단답형 비율을 늘리면 비용을 90% 절감할 수 있습니다',
                'potential_savings': essay_cost * 0.9
            })

        # 2. 캐싱 효과 확인
        summary_count = breakdown['count_by_operation'].get('summary_long', 0) + \
                        breakdown['count_by_operation'].get('summary_short', 0)

        if summary_count > 1:
            suggestions.append({
                'type': 'optimization',
                'severity': 'medium',
                'message': f'동일 문서를 {summary_count}번 요약했습니다',
                'recommendation': '캐싱 시스템을 활용하면 중복 요약을 방지할 수 있습니다',
                'potential_savings': breakdown['by_operation'].get('summary_long', 0) * 0.9
            })

        # 3. Google OCR 사용률
        ocr_cost = breakdown['by_operation'].get('google_ocr', 0)
        if ocr_cost > 0:
            ocr_ratio = ocr_cost / breakdown['total']
            if ocr_ratio < 0.1:
                suggestions.append({
                    'type': 'info',
                    'severity': 'low',
                    'message': f'Google OCR 비용이 낮습니다 (${ocr_cost:.2f}, {ocr_ratio*100:.1f}%)',
                    'recommendation': 'PyMuPDF fallback 전략이 잘 작동하고 있습니다'
                })

        # 4. 총 비용 경고
        if breakdown['total'] > 1.0:
            suggestions.append({
                'type': 'alert',
                'severity': 'high',
                'message': f'세션 총 비용이 $1를 초과했습니다 (${breakdown["total"]:.2f})',
                'recommendation': '비용이 높습니다. 퀴즈 설정을 검토하세요'
            })

        return suggestions

    def get_dashboard_data(self, timeframe: str = '7days') -> dict:
        """대시보드 데이터"""

        # 기간 설정
        if timeframe == '7days':
            start_date = datetime.now() - timedelta(days=7)
        elif timeframe == '30days':
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = datetime.now() - timedelta(days=1)

        logs = self.db.get_cost_logs_since(start_date)

        # 일별 집계
        daily_costs = defaultdict(float)
        for log in logs:
            date = log['timestamp'].date()
            daily_costs[date] += log['cost']

        # 작업별 집계
        operation_costs = defaultdict(float)
        for log in logs:
            operation_costs[log['operation']] += log['cost']

        total_cost = sum(log['cost'] for log in logs)

        return {
            'timeframe': timeframe,
            'total_cost': total_cost,
            'avg_daily_cost': total_cost / len(daily_costs) if daily_costs else 0,
            'daily_costs': dict(daily_costs),
            'operation_costs': dict(operation_costs),
            'top_operations': sorted(
                operation_costs.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'optimization_potential': self._estimate_optimization_potential(logs)
        }

    def _estimate_optimization_potential(self, logs: List[dict]) -> float:
        """최적화 가능 금액 추정"""

        # 주관식 → 단답형/객관식으로 전환 시
        essay_cost = sum(log['cost'] for log in logs if log['operation'] == 'essay_grading')
        potential_savings = essay_cost * 0.8  # 80% 절감 가능

        # 중복 요약
        summary_ops = [log for log in logs if 'summary' in log['operation']]
        if len(summary_ops) > 1:
            potential_savings += sum(log['cost'] for log in summary_ops[1:]) * 0.9

        return potential_savings
```

---

## 4. 개발 로드맵 (7일)

### 📅 Day 1-2: 퀴즈 시스템 고도화 (16시간)

**Day 1 (8h)**
- ✅ 퀴즈 모델 확장 (Pydantic)
  * QuizConfig 클래스
  * 4가지 문제 유형 스키마
- ✅ 프롬프트 작성
  * 단답형 생성 프롬프트
  * O/X 생성 프롬프트
  * 주관식 생성 프롬프트 (평가 기준 포함)
- ✅ DiagnosisAgent 대폭 개선
  * 유형별 문제 생성
  * 비율 기반 문제 배분

**Day 2 (8h)**
- ✅ AI 채점 엔진 구현
  * ShortAnswerGrader (하이브리드)
  * EssayGrader (GPT-4)
- ✅ GradingEngine 통합
  * 유형별 라우팅
  * 결과 표준화
- ✅ 테스트 및 검증
  * 채점 정확도 테스트
  * 성능 측정

---

### 📅 Day 3: OCR & RAG 고도화 (8시간)

**OCR (4h)**
- ✅ SmartOCRService 구현
  * PyMuPDF → Google Vision
  * 품질 검증 로직
  * 비용 추적

**RAG (4h)**
- ✅ Perplexity 스타일 답변없음
  * 추천 질문 생성
  * 공식 소스 매핑
  * 대체 행동 제안
- ✅ UI 구현 (Streamlit)

---

### 📅 Day 4-5: 학습 분석 시스템 (16시간)

**Day 4 (8h)**
- ✅ LearningAnalyzer
  * 퀴즈 성과 분석
  * 학습 패턴 분석
  * 약점/강점 파악
- ✅ WrongAnswerNotebook
  * 오답 노트 생성
  * 복습 우선순위 계산

**Day 5 (8h)**
- ✅ WeaknessTargetedQuizzer
  * 약점 집중 퀴즈 생성
- ✅ ProgressVisualizer
  * 진도율 계산
  * 대시보드 데이터
- ✅ 대시보드 UI (Streamlit)
  * 차트 (Plotly)
  * 통계 표시

---

### 📅 Day 6: 비용 최적화 & 고급 UI (8시간)

- ✅ AdvancedCostMonitor (4h)
  * 실시간 추적
  * 최적화 제안
  * 대시보드
- ✅ 고급 UI 개선 (4h)
  * 퀴즈 설정 UI
  * 진도율 대시보드
  * 오답 노트 UI

---

### 📅 Day 7: 통합 테스트 & 문서화 (8시간)

- ✅ E2E 테스트 (4h)
  * 전체 시나리오
  * 성능 측정
  * 비용 검증
- ✅ 문서 업데이트 (4h)
  * README.md
  * API 문서
  * 사용 가이드

---

## 5. 기술 스택 추가

```txt
# v2.0 기본 (유지)
fastapi==0.104.1
uvicorn==0.24.0
pymupdf==1.26.5
openai==1.54.0
chromadb==0.4.22
streamlit==1.31.0
aiosqlite==0.19.0
tenacity==8.2.3
tiktoken==0.5.1
wikipedia-api==0.6.0

# v2.0 고급 (추가)
google-cloud-vision==3.5.0  # Google OCR
plotly==5.18.0              # 대시보드 차트
pandas==2.1.4               # 데이터 분석
numpy==1.26.2               # 통계 계산
scikit-learn==1.3.2         # 유사도 계산 (선택)
```

---

## 6. 폴더 구조 (확장)

```
SynapseSimple/
├── backend/
│   ├── agents/
│   │   ├── summary_agent.py
│   │   ├── diagnosis_agent.py      # 대폭 개선 ⭐⭐⭐
│   │   ├── planning_agent.py
│   │   └── evaluation_agent.py     # NEW ⭐
│   │
│   ├── services/
│   │   ├── smart_ocr_service.py    # NEW ⭐⭐
│   │   ├── grading_engine.py       # NEW ⭐⭐⭐
│   │   ├── rag_service.py          # 개선 ⭐
│   │   └── ...
│   │
│   ├── analytics/                  # NEW ⭐⭐⭐
│   │   ├── learning_analyzer.py
│   │   ├── wrong_answer_notebook.py
│   │   ├── weakness_quizzer.py
│   │   ├── progress_visualizer.py
│   │   └── cost_monitor.py
│   │
│   ├── models/
│   │   ├── quiz_models.py          # 확장 ⭐
│   │   └── ...
│   │
│   └── ...
│
├── frontend/
│   ├── pages/
│   │   ├── 2_Diagnosis.py          # 대폭 개선 ⭐⭐⭐
│   │   ├── 3_QA.py                 # Perplexity 스타일 ⭐⭐
│   │   ├── 5_Dashboard.py          # 시각화 강화 ⭐⭐⭐
│   │   └── 7_WrongNote.py          # NEW ⭐⭐
│   │
│   ├── components/
│   │   ├── quiz_config_widget.py   # NEW ⭐
│   │   ├── chart_widgets.py        # NEW ⭐⭐
│   │   └── ...
│   │
│   └── ...
│
└── ...
```

---

## 7. 성공 지표 (KPI)

### 기능 달성
✅ **퀴즈 유형**: 4가지 (객관식/단답형/O/X/주관식)
✅ **AI 채점 정확도**: 90%+ (단답형/주관식)
✅ **답변 없음 처리**: 100% (Perplexity 스타일)
✅ **약점 진단 정확도**: 85%+
✅ **OCR fallback 성공률**: 98%+

### 성능
- 단답형 채점: <3초
- 주관식 채점: <10초
- 추천 질문 생성: <2초
- 대시보드 로딩: <1초
- OCR (Google Vision): 3-5초

### 사용자 경험
- 퀴즈 설정 자유도: ⭐⭐⭐⭐⭐
- 채점 피드백 상세도: ⭐⭐⭐⭐⭐
- 학습 분석 유용성: ⭐⭐⭐⭐⭐

---

## 8. 비용 예산 (고급)

### 100명/월 기준

**v2.0 기본** ($19)
- 임베딩: $2
- 요약: $6
- Q&A: $8
- 기본 퀴즈: $3

**v2.0 고급 추가**
- 단답형 AI 채점 (30% AI 사용): $5
- 주관식 채점 (10% 비율): $15
- 답변없음 추천질문: $2
- Google OCR (10% fallback): $1
- 약점 퀴즈 생성: $3
- 학습 분석: $1

**총: $42/월**
**사용자당: $0.42**

### 최적화 효과

```
최적화 전 (순진한 방법):
- 모든 단답형 AI 채점: $15
- 모든 PDF Google OCR: $10
- 총: $80/월

최적화 후 (스마트 전략):
- 단답형 하이브리드: $5 (67% 절감)
- OCR Fallback: $1 (90% 절감)
- 총: $42/월 (47.5% 절감)
```

---

## 9. v3.0 차세대 기능 예고 🎙️

### 4단계: 음성 인터페이스 (미래 계획)

#### 4.1 요약 TTS (Text-to-Speech)
```python
# OpenAI TTS API
summary_audio = openai.Audio.create(
    model="tts-1",
    voice="alloy",
    input=summary_text
)

# 사용자가 듣기
st.audio(summary_audio, format='audio/mp3')
```

#### 4.2 대화 요약 팟캐스트 (2명 대화)
```python
# 2명 음성으로 대화형 요약
podcast = create_podcast_dialogue(
    conversation_summary,
    voice1="alloy",  # 선생님
    voice2="echo"    # 학생
)

# 예시:
# 선생님: "오늘 학습한 토마토 재배의 핵심은..."
# 학생: "아, 그렇군요! 특히 물주기가 중요하다는 거죠?"
```

#### 4.3 학습 내용 오디오북
```python
# 전체 학습 자료를 오디오북으로
audiobook = convert_to_audiobook(
    document_text,
    chapters=key_concepts,
    voice="nova"
)
```

#### 4.4 음성 질문 (STT)
```python
# 음성으로 질문
audio_input = st.audio_input("질문하세요")

# STT로 변환
question = openai.Audio.transcribe(
    model="whisper-1",
    file=audio_input
)

# RAG 답변
answer = rag_service.answer(question)

# TTS로 답변
answer_audio = openai.Audio.create(
    model="tts-1",
    voice="alloy",
    input=answer
)
```

### 음성 기능 비용 예상
```
TTS: $0.015 / 1K characters
STT: $0.006 / minute

예시 (100명/월):
- 요약 TTS (500자): $0.75
- 질문 STT (1분): $0.60
- 답변 TTS (300자): $0.45
- 총: $2/월 (추가)
```

---

## 10. 참고 자료

### 프로젝트 문서
- **v1.0 완료**: PROJECT_COMPLETE_V1.md
- **v2.0 기본**: PROJECT_ROADMAP_V2_BASIC.md
- **v2.0 고급**: 본 문서

### 기술 문서
- **OpenAI API**: https://platform.openai.com/docs
- **Google Cloud Vision**: https://cloud.google.com/vision/docs
- **Plotly**: https://plotly.com/python/
- **Streamlit**: https://docs.streamlit.io

---

## 11. 작성 정보

**문서명**: PROJECT_ROADMAP_V2_ADVANCED.md
**버전**: 1.0
**작성일**: 2025-10-18
**작성자**: FastCampus Project Team
**상태**: ✅ 최종 확정

**다음 단계**
1. ✅ v2.0 기본 계획 완료
2. ✅ v2.0 고급 계획 완료
3. ⏳ v2.0 개발 시작

---

**프로젝트 상태**: 🚀 **v2.0 고급 계획 완료**
**다음 목표**: v2.0 개발 시작 (기본 → 고급)
