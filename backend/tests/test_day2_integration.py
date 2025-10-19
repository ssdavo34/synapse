"""
Day 2 Integration Tests - SynapseSimple v2.0

Tests for all Day 2 services:
1. OpenAI Client
2. Embedding Service
3. Text Processor
4. OCR Service
5. File Validator
6. Wikipedia Service
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from backend.services.openai_client import OpenAIClient
from backend.services.embedding_service import EmbeddingService
from backend.utils.text_processor import TextProcessor
from backend.services.ocr_service import OCRService
from backend.services.file_validator import FileValidator
from backend.services.wikipedia_service import WikipediaService


class TestOpenAIClient:
    """Test OpenAI Client basic functionality"""

    @pytest.fixture
    def client(self):
        return OpenAIClient()

    def test_create_completion(self, client):
        """Test simple Hello response"""
        response = client.create_completion("Say Hello in one word")

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\nOpenAI Response: {response}")


class TestEmbeddingService:
    """Test Embedding Service"""

    @pytest.fixture
    def service(self):
        return EmbeddingService()

    def test_create_embedding(self, service):
        """Test 1536-dimension vector generation"""
        text = "This is a test sentence for embedding."
        embedding = service.create_embedding(text)

        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)
        print(f"\nEmbedding dimension: {len(embedding)}")

    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]

        similarity_same = EmbeddingService.cosine_similarity(vec1, vec2)
        similarity_ortho = EmbeddingService.cosine_similarity(vec1, vec3)

        assert abs(similarity_same - 1.0) < 0.0001
        assert abs(similarity_ortho - 0.0) < 0.0001
        print(f"\nSame vectors: {similarity_same}, Orthogonal: {similarity_ortho}")


class TestTextProcessor:
    """Test Text Processor"""

    @pytest.fixture
    def processor(self):
        return TextProcessor()

    def test_chunk_text(self, processor):
        """Test text chunking functionality"""
        text = "This is a test. " * 100
        chunks = processor.chunk_text(text, chunk_size=50, overlap=10)

        assert chunks is not None
        assert isinstance(chunks, list)
        assert len(chunks) > 1
        assert all(isinstance(chunk, str) for chunk in chunks)
        print(f"\nNumber of chunks: {len(chunks)}")

    def test_clean_text(self, processor):
        """Test text cleaning"""
        dirty_text = "  Hello\n\n\nWorld  \t\t  "
        clean_text = processor.clean_text(dirty_text)

        assert clean_text is not None
        assert isinstance(clean_text, str)
        print(f"\nOriginal: '{dirty_text}'")
        print(f"Cleaned: '{clean_text}'")


class TestOCRService:
    """Test OCR Service"""

    @pytest.fixture
    def service(self):
        return OCRService()

    def test_extract_text_from_invalid_pdf(self, service):
        """Test handling of nonexistent PDF file"""
        result = service.extract_text_from_pdf("nonexistent.pdf")

        assert result is not None
        assert isinstance(result, dict)
        assert "error" in result or "text" in result
        print(f"\nInvalid PDF result: {result}")

    def test_validate_pdf_path(self, service):
        """Test PDF path validation"""
        assert not service._is_valid_pdf_path("notapdf.txt")
        assert not service._is_valid_pdf_path("")
        assert service._is_valid_pdf_path("document.pdf")
        assert service._is_valid_pdf_path("/path/to/file.PDF")
        print("\nPDF path validation works correctly")


class TestFileValidator:
    """Test File Validator"""

    @pytest.fixture
    def validator(self):
        return FileValidator()

    def test_validate_file_extension(self, validator):
        """Test file extension validation"""
        assert validator.validate_extension("document.pdf")
        assert validator.validate_extension("text.txt")
        assert not validator.validate_extension("script.exe")
        assert not validator.validate_extension("noextension")
        print("\nFile extension validation passed")

    def test_validate_file_size(self, validator):
        """Test file size validation logic"""
        max_size = 10 * 1024 * 1024

        assert validator._is_size_valid(5 * 1024 * 1024, max_size)
        assert not validator._is_size_valid(15 * 1024 * 1024, max_size)
        print("\nFile size validation passed")


class TestWikipediaService:
    """Test Wikipedia Service"""

    @pytest.fixture
    def service(self):
        return WikipediaService()

    def test_search_wikipedia(self, service):
        """Test Wikipedia search returns results"""
        query = "Python programming language"
        results = service.search(query, max_results=3)

        assert results is not None
        assert isinstance(results, list)
        assert len(results) >= 1

        if results:
            first_result = results[0]
            assert "title" in first_result
            assert "summary" in first_result or "text" in first_result
            print(f"\nSearch query: {query}")
            print(f"Number of results: {len(results)}")
            print(f"First result title: {first_result.get('title', 'N/A')}")


def test_all_services_import():
    """Test that all Day 2 services can be imported"""
    assert OpenAIClient is not None
    assert EmbeddingService is not None
    assert TextProcessor is not None
    assert OCRService is not None
    assert FileValidator is not None
    assert WikipediaService is not None
    print("\nAll Day 2 services imported successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
