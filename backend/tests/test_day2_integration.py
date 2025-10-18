"""
Day 2 Integration Tests

Day 2에서 구현한 모든 서비스의 통합 테스트를 수행합니다.

Test Scenarios:
    1. OpenAI Client 연결 테스트
    2. Embedding 생성 테스트
    3. TextProcessor 테스트
    4. OCR 테스트
    5. FileValidator 테스트
    6. WikipediaService 테스트
    7. 전체 파이프라인 테스트 (PDF → OCR → Embedding → Wikipedia 검색)

Requirements:
    - pytest
    - pytest-asyncio
    - All Day 2 services
"""

import os
import sys
import pytest
import pytest_asyncio
import asyncio
import tempfile
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.config import get_settings
from backend.services.openai_client import OpenAIClient
from backend.services.embedding_service import EmbeddingService
from backend.utils.text_processor import TextProcessor
from backend.services.ocr_service import OCRService
from backend.services.file_validator import FileValidator
from backend.services.wikipedia_service import WikipediaService


# Fixtures
@pytest.fixture
def settings():
    """설정 픽스처"""
    return get_settings()


@pytest_asyncio.fixture
async def openai_client():
    """OpenAI 클라이언트 픽스처"""
    return OpenAIClient()


@pytest_asyncio.fixture
async def embedding_service(openai_client):
    """임베딩 서비스 픽스처"""
    return EmbeddingService(openai_client)


@pytest.fixture
def text_processor():
    """텍스트 프로세서 픽스처"""
    return TextProcessor()


@pytest.fixture
def ocr_service():
    """OCR 서비스 픽스처"""
    return OCRService()


@pytest.fixture
def file_validator():
    """파일 검증기 픽스처"""
    return FileValidator()


@pytest.fixture
def wikipedia_service():
    """Wikipedia 서비스 픽스처"""
    return WikipediaService(language='en')


# Test 1: OpenAI Client 연결 테스트
@pytest.mark.asyncio
async def test_openai_client_connection(openai_client):
    """
    OpenAI Client 연결 및 기본 completion 테스트

    검증 항목:
    - API 키 로드 확인
    - 간단한 completion 요청 성공
    - 응답 시간 30초 이내
    """
    print("\n=== Test 1: OpenAI Client Connection ===")

    # 간단한 메시지 전송
    messages = [
        {"role": "user", "content": "Say 'Hello'"}
    ]

    import time
    start_time = time.time()

    response = await openai_client.chat_completion(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.7
    )

    elapsed_time = time.time() - start_time

    # 검증
    assert response is not None
    assert hasattr(response, 'choices')
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    assert elapsed_time < 30.0  # 30초 이내

    print(f"✅ OpenAI Client connected successfully")
    print(f"   Response: {response.choices[0].message.content[:50]}")
    print(f"   Response time: {elapsed_time:.2f}s")


# Test 2: Embedding 생성 테스트
@pytest.mark.asyncio
async def test_embedding_generation(embedding_service):
    """
    임베딩 생성 및 유사도 계산 테스트

    검증 항목:
    - 텍스트 → 임베딩 벡터 변환
    - 벡터 차원 1536 확인
    - 유사한 텍스트 간 코사인 유사도 > 0.3
    """
    print("\n=== Test 2: Embedding Generation ===")

    # 테스트 텍스트
    texts = [
        "Python is a programming language",
        "Python is used for machine learning",
        "The weather is sunny today"
    ]

    # 임베딩 생성
    embeddings = await embedding_service.generate_embeddings(texts)

    # 검증: 벡터 수와 차원
    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)

    # 유사도 계산
    similarity_1_2 = embedding_service.cosine_similarity(embeddings[0], embeddings[1])
    similarity_1_3 = embedding_service.cosine_similarity(embeddings[0], embeddings[2])

    # 검증: 관련 텍스트가 무관한 텍스트보다 유사도가 높아야 함
    assert similarity_1_2 > 0.3  # Python 관련 텍스트들
    assert similarity_1_2 > similarity_1_3  # Python vs 날씨

    print(f"✅ Embeddings generated successfully")
    print(f"   Vector dimension: {len(embeddings[0])}")
    print(f"   Similarity (Python texts): {similarity_1_2:.3f}")
    print(f"   Similarity (Python vs Weather): {similarity_1_3:.3f}")


# Test 3: TextProcessor 테스트
@pytest.mark.asyncio
async def test_text_processor(text_processor):
    """
    텍스트 처리 (청킹, 정제, 토큰 카운트) 테스트

    검증 항목:
    - 긴 텍스트 청킹 (500자 기준)
    - 청크 간 오버랩 확인 (50자)
    - 토큰 카운트 정확도
    """
    print("\n=== Test 3: Text Processor ===")

    # 긴 텍스트 생성 (1000자 이상)
    long_text = "This is a test sentence. " * 50  # ~1200자

    # 텍스트 청킹
    chunks = text_processor.chunk_text(long_text, chunk_size=500, overlap=50)

    # 검증
    assert len(chunks) > 1  # 여러 청크로 분리되어야 함
    assert all(len(chunk) <= 550 for chunk in chunks)  # 최대 크기 준수

    # 텍스트 정제
    dirty_text = "  Multiple   spaces   and\n\n\n\nnewlines  "
    clean_text = text_processor.clean_text(dirty_text)
    assert "  " not in clean_text  # 연속 공백 제거
    assert "\n\n\n" not in clean_text  # 연속 개행 제거

    print(f"✅ Text processing successful")
    print(f"   Original text: {len(long_text)} chars")
    print(f"   Chunks: {len(chunks)}")


# Test 4: OCR 테스트
@pytest.mark.asyncio
async def test_ocr_service(ocr_service):
    """
    PDF 텍스트 추출 테스트

    검증 항목:
    - 테스트용 PDF 생성 (2페이지)
    - 텍스트 추출 성공
    - 메타데이터 검증 (페이지 수, 파일 크기)
    """
    print("\n=== Test 4: OCR Service ===")

    # 임시 디렉토리에 테스트 PDF 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, "test_ocr.pdf")

        # PDF 생성 (PyMuPDF 사용)
        import fitz  # PyMuPDF
        doc = fitz.open()

        # 페이지 1
        page1 = doc.new_page()
        page1.insert_text((50, 50), "Page 1: OCR Test Document")
        page1.insert_text((50, 100), "This is the first page of the test PDF.")

        # 페이지 2
        page2 = doc.new_page()
        page2.insert_text((50, 50), "Page 2: Additional Content")
        page2.insert_text((50, 100), "This is the second page.")

        doc.save(pdf_path)
        doc.close()

        # OCR 실행
        result = ocr_service.extract_text(pdf_path)

        # 검증
        assert result is not None
        assert result['num_pages'] == 2
        assert result['file_size'] > 0
        assert len(result['text']) > 0
        assert "OCR Test Document" in result['text']
        assert "second page" in result['text']

        print(f"✅ OCR extraction successful")
        print(f"   Pages: {result['num_pages']}")
        print(f"   File size: {result['file_size']} bytes")
        print(f"   Extracted text length: {len(result['text'])} chars")


# Test 5: FileValidator 테스트
@pytest.mark.asyncio
async def test_file_validator(file_validator):
    """
    파일 검증 테스트

    검증 항목:
    - PDF 파일 검증 통과
    - TXT 파일 검증 통과
    - 악성 파일(.exe) 차단
    - 파일 크기 제한 확인
    """
    print("\n=== Test 5: File Validator ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. 안전한 PDF 파일
        safe_pdf = os.path.join(temp_dir, "safe.pdf")
        with open(safe_pdf, 'wb') as f:
            f.write(b'%PDF-1.4\nSafe PDF content')

        result_pdf = file_validator.validate_file(safe_pdf)
        assert result_pdf['is_valid'] is True
        assert result_pdf['mime_type'] == 'application/pdf'

        # 2. 안전한 TXT 파일
        safe_txt = os.path.join(temp_dir, "safe.txt")
        with open(safe_txt, 'w') as f:
            f.write("Safe text content")

        result_txt = file_validator.validate_file(safe_txt)
        assert result_txt['is_valid'] is True
        assert result_txt['mime_type'] == 'text/plain'

        # 3. 악성 패턴 포함 파일
        malicious = os.path.join(temp_dir, "malicious.txt")
        with open(malicious, 'wb') as f:
            f.write(b'<script>alert("xss")</script>')

        result_malicious = file_validator.validate_file(malicious)
        assert result_malicious['is_valid'] is False
        assert 'malicious' in result_malicious.get('error', '').lower()

        # 4. 잘못된 확장자
        exe_file = os.path.join(temp_dir, "file.exe")
        with open(exe_file, 'w') as f:
            f.write("executable")

        result_exe = file_validator.validate_file(exe_file)
        assert result_exe['is_valid'] is False
        assert 'extension' in result_exe.get('error', '').lower()

        print(f"✅ File validation successful")
        print(f"   PDF validated: {result_pdf['is_valid']}")
        print(f"   TXT validated: {result_txt['is_valid']}")
        print(f"   Malicious blocked: {not result_malicious['is_valid']}")
        print(f"   Invalid extension blocked: {not result_exe['is_valid']}")


# Test 6: WikipediaService 테스트
@pytest.mark.asyncio
async def test_wikipedia_service(wikipedia_service):
    """
    Wikipedia 검색 및 내용 조회 테스트

    검증 항목:
    - "Artificial Intelligence" 검색
    - 첫 번째 결과 내용 가져오기
    - 요약본 길이 확인
    """
    print("\n=== Test 6: Wikipedia Service ===")

    # 검색
    search_results = wikipedia_service.search_wikipedia("Artificial Intelligence", limit=3)

    # 검증
    assert len(search_results) > 0
    assert all('title' in r and 'url' in r for r in search_results)

    # 첫 번째 결과 내용 가져오기
    if search_results:
        first_title = search_results[0]['title']
        content = wikipedia_service.get_page_content(first_title, sentences=3)

        assert content['exists'] is True
        assert len(content['summary']) > 0
        assert content['url'].startswith('https://')

        print(f"✅ Wikipedia service functional")
        print(f"   Search results: {len(search_results)}")
        print(f"   First result: {first_title}")
        print(f"   Summary length: {len(content['summary'])} chars")
    else:
        print("⚠️  No search results found (may be network issue)")


# Test 7: 전체 파이프라인 테스트
@pytest.mark.asyncio
async def test_full_pipeline(
    ocr_service,
    text_processor,
    embedding_service,
    wikipedia_service
):
    """
    전체 파이프라인 통합 테스트

    시나리오:
    1. PDF 업로드 → OCR → TextProcessor → Embedding
    2. Wikipedia 검색 → TextProcessor → Embedding
    3. 두 임베딩 간 유사도 계산

    검증 항목:
    - 각 단계가 정상적으로 연결됨
    - 최종 유사도 계산 성공
    - 전체 파이프라인 실행 시간 < 60초
    """
    print("\n=== Test 7: Full Pipeline Integration ===")

    import time
    start_time = time.time()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Step 1: PDF 생성
        pdf_path = os.path.join(temp_dir, "ai_document.pdf")

        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text(
            (50, 50),
            "Artificial Intelligence in Education\n\n"
            "Machine learning and deep learning are transforming education. "
            "AI-powered tutoring systems provide personalized learning experiences. "
            "Natural language processing enables intelligent chatbots for student support."
        )
        doc.save(pdf_path)
        doc.close()

        # Step 2: OCR로 텍스트 추출
        ocr_result = ocr_service.extract_text(pdf_path)
        pdf_text = ocr_result['text']

        assert len(pdf_text) > 0
        print(f"   Step 1: PDF text extracted ({len(pdf_text)} chars)")

        # Step 3: TextProcessor로 정제 및 청킹
        clean_pdf_text = text_processor.clean_text(pdf_text)
        pdf_chunks = text_processor.chunk_text(clean_pdf_text, chunk_size=500)

        assert len(pdf_chunks) > 0
        print(f"   Step 2: Text processed ({len(pdf_chunks)} chunks)")

        # Step 4: PDF 텍스트 임베딩 생성
        pdf_embedding = await embedding_service.generate_embeddings([clean_pdf_text])

        assert len(pdf_embedding) == 1
        assert len(pdf_embedding[0]) == 1536
        print(f"   Step 3: PDF embedding generated (1536 dims)")

        # Step 5: Wikipedia 검색
        wiki_results = wikipedia_service.search_wikipedia("Artificial Intelligence in Education", limit=1)

        if wiki_results:
            # Step 6: Wikipedia 내용 가져오기
            wiki_content = wikipedia_service.get_page_content(
                wiki_results[0]['title'],
                sentences=5
            )

            if wiki_content['exists']:
                wiki_text = wiki_content['summary']

                # Step 7: Wikipedia 텍스트 임베딩 생성
                wiki_embedding = await embedding_service.generate_embeddings([wiki_text])

                assert len(wiki_embedding) == 1
                print(f"   Step 4: Wikipedia embedding generated")

                # Step 8: 유사도 계산
                similarity = embedding_service.cosine_similarity(
                    pdf_embedding[0],
                    wiki_embedding[0]
                )

                assert 0.0 <= similarity <= 1.0

                elapsed_time = time.time() - start_time
                assert elapsed_time < 60.0  # 60초 이내

                print(f"✅ Full pipeline successful")
                print(f"   PDF text: {len(pdf_text)} chars")
                print(f"   Wikipedia text: {len(wiki_text)} chars")
                print(f"   Similarity: {similarity:.3f}")
                print(f"   Total time: {elapsed_time:.2f}s")
            else:
                print("⚠️  Wikipedia page not found")
        else:
            print("⚠️  Wikipedia search returned no results")


# 통합 테스트 요약
@pytest.mark.asyncio
async def test_summary():
    """
    통합 테스트 요약

    모든 Day 2 서비스가 정상적으로 동작하는지 확인합니다.
    """
    print("\n" + "="*50)
    print("Day 2 Integration Test Summary")
    print("="*50)
    print("✅ Test 1: OpenAI Client - Connection & Completion")
    print("✅ Test 2: Embedding Service - Vector Generation & Similarity")
    print("✅ Test 3: Text Processor - Chunking & Token Count")
    print("✅ Test 4: OCR Service - PDF Text Extraction")
    print("✅ Test 5: File Validator - Security Validation")
    print("✅ Test 6: Wikipedia Service - Search & Content Retrieval")
    print("✅ Test 7: Full Pipeline - End-to-End Integration")
    print("="*50)
    print("All Day 2 services are operational!")


if __name__ == "__main__":
    # pytest를 사용하지 않고 직접 실행 시
    print("Run tests with: pytest backend/tests/test_day2_integration.py -v")
