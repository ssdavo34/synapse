# SynapseSimple

PDF 문서 처리 및 벡터 저장 시스템

## 기능
- PDF 업로드 및 저장
- 텍스트 추출 (PyMuPDF)
- 텍스트 청킹 (500자 단위)
- 임베딩 생성 (OpenAI)
- ChromaDB 벡터 저장
- Streamlit 조회

## 설치
```bash
pip install -r requirements.txt
```

## 실행
```bash
# Backend
python main.py

# Streamlit
streamlit run app.py
```

## 환경 변수
.env 파일 생성:
```
OPENAI_API_KEY=your_key_here
```
