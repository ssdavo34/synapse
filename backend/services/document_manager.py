"""
Document Manager for SynapseSimple v2.0

Complete document processing pipeline:
1. File validation
2. Database record creation
3. OCR text extraction
4. Text chunking
5. Embedding generation
6. Vector storage
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional, List
import hashlib
import shutil
import os
from datetime import datetime

from services.database_service import db_service
from services.file_validator import FileValidator
from services.ocr_service import OCRService
from utils.text_processor import TextProcessor
from services.embedding_service import EmbeddingService
from services.vector_store_service import vector_store_service
from utils.logger import setup_logger
from config import settings


class DocumentManager:
    """Manages complete document processing pipeline"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.file_validator = FileValidator()
        self.ocr_service = OCRService()
        self.text_processor = TextProcessor()
        self.embedding_service = EmbeddingService()
        self.vector_service = vector_store_service

        # Ensure upload directory exists
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Document Manager initialized")

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def _save_uploaded_file(self, file_path: str, user_id: int) -> str:
        """Save uploaded file to storage"""
        # Create user directory
        user_dir = self.upload_dir / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename with timestamp
        original_name = Path(file_path).name
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{timestamp}_{original_name}"
        destination = user_dir / new_filename

        # Copy file
        shutil.copy2(file_path, destination)

        self.logger.info(f"File saved: {destination}")
        return str(destination)

    async def upload_document(
        self,
        file_path: str,
        user_id: int,
        title: Optional[str] = None,
        check_duplicate: bool = True
    ) -> Dict[str, Any]:
        """
        Upload and process a document through complete pipeline

        Args:
            file_path: Path to the file to upload
            user_id: User ID
            title: Document title (optional, uses filename if not provided)
            check_duplicate: Check for duplicate files

        Returns:
            Result dict with document_id and processing status
        """
        try:
            self.logger.info(f"📄 Starting document upload: {file_path}")

            # Step 1: File validation
            self.logger.info("Step 1/7: Validating file...")
            validation_result = self.file_validator.validate_file(file_path)

            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "error": validation_result.get("error", "File validation failed"),
                    "step": "validation"
                }

            # Get file metadata
            file_size = os.path.getsize(file_path)
            file_type = validation_result["mime_type"]
            file_name = Path(file_path).name

            if title is None:
                title = Path(file_path).stem

            # Step 2: Check for duplicates
            file_hash = None
            if check_duplicate:
                self.logger.info("Step 2/7: Checking for duplicates...")
                file_hash = self._calculate_file_hash(file_path)

                existing_doc = db_service.get_document_by_hash(file_hash, user_id)
                if existing_doc:
                    self.logger.warning(f"Duplicate file detected: {existing_doc.id}")
                    return {
                        "success": False,
                        "error": "Document already exists",
                        "duplicate": True,
                        "existing_document_id": existing_doc.id,
                        "step": "duplicate_check"
                    }

            # Step 3: Save file to storage
            self.logger.info("Step 3/7: Saving file...")
            saved_path = self._save_uploaded_file(file_path, user_id)

            # Step 4: Create database record
            self.logger.info("Step 4/7: Creating database record...")
            document = db_service.create_document(
                user_id=user_id,
                title=title,
                file_path=saved_path,
                file_type=file_type,
                file_size=file_size,
                file_hash=file_hash
            )

            # Update status to processing
            db_service.update_document(document.id, status="processing")

            # Step 5: Extract text with OCR
            self.logger.info("Step 5/7: Extracting text...")
            try:
                ocr_result = self.ocr_service.extract_text_from_pdf(saved_path)

                if "error" in ocr_result:
                    raise Exception(ocr_result["error"])

                full_text = ocr_result["text"]
                page_count = ocr_result.get("num_pages", 0)

                # Update document with extracted text
                db_service.update_document(
                    document.id,
                    full_text=full_text,
                    text_length=len(full_text),
                    page_count=page_count
                )

            except Exception as e:
                self.logger.error(f"OCR failed: {e}")
                db_service.update_document(
                    document.id,
                    status="failed",
                    error_message=f"Text extraction failed: {str(e)}"
                )
                return {
                    "success": False,
                    "error": f"Text extraction failed: {str(e)}",
                    "document_id": document.id,
                    "step": "ocr"
                }

            # Step 6: Chunk text
            self.logger.info("Step 6/7: Chunking text...")
            try:
                chunks = self.text_processor.chunk_text(
                    full_text,
                    chunk_size=500,
                    overlap=50
                )

                if not chunks:
                    raise Exception("No chunks created from text")

                # Create chunk records in database
                chunks_data = []
                for index, chunk_content in enumerate(chunks):
                    token_count = self.text_processor.count_tokens(chunk_content)
                    char_count = len(chunk_content)

                    chunks_data.append({
                        "document_id": document.id,
                        "content": chunk_content,
                        "chunk_index": index,
                        "token_count": token_count,
                        "char_count": char_count
                    })

                # Bulk insert chunks
                created_chunks = db_service.create_chunks_bulk(chunks_data)

                # Update document chunk count
                db_service.update_document(
                    document.id,
                    chunk_count=len(created_chunks)
                )

                self.logger.info(f"Created {len(created_chunks)} chunks")

            except Exception as e:
                self.logger.error(f"Chunking failed: {e}")
                db_service.update_document(
                    document.id,
                    status="failed",
                    error_message=f"Text chunking failed: {str(e)}"
                )
                return {
                    "success": False,
                    "error": f"Text chunking failed: {str(e)}",
                    "document_id": document.id,
                    "step": "chunking"
                }

            # Step 7: Generate embeddings and store vectors
            self.logger.info("Step 7/7: Generating embeddings and storing vectors...")
            try:
                # Prepare chunks for vector service
                chunks_for_vectors = [
                    {
                        "id": chunk.id,
                        "document_id": chunk.document_id,
                        "content": chunk.content,
                        "chunk_index": chunk.chunk_index,
                        "token_count": chunk.token_count
                    }
                    for chunk in created_chunks
                ]

                # Generate embeddings and upsert to vector store
                vector_count = await self.vector_service.upsert_chunks(chunks_for_vectors)

                # Update chunks with embedding status
                for chunk in created_chunks:
                    db_service.update_chunk(
                        chunk.id,
                        has_embedding=True,
                        vector_id=f"chunk_{chunk.id}"
                    )

                self.logger.info(f"Stored {vector_count} vectors")

            except Exception as e:
                self.logger.error(f"Embedding generation failed: {e}")
                db_service.update_document(
                    document.id,
                    status="failed",
                    error_message=f"Embedding generation failed: {str(e)}"
                )
                return {
                    "success": False,
                    "error": f"Embedding generation failed: {str(e)}",
                    "document_id": document.id,
                    "step": "embedding"
                }

            # Mark document as completed
            db_service.update_document(document.id, status="completed")

            self.logger.info(f"✅ Document processing completed: {document.id}")

            return {
                "success": True,
                "document_id": document.id,
                "title": title,
                "chunk_count": len(created_chunks),
                "vector_count": vector_count,
                "page_count": page_count,
                "text_length": len(full_text),
                "file_size": file_size,
                "file_type": file_type
            }

        except Exception as e:
            self.logger.error(f"Document upload failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "step": "unknown"
            }

    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get document details"""
        try:
            document = db_service.get_document(document_id)
            if not document:
                return None

            return {
                "id": document.id,
                "user_id": document.user_id,
                "title": document.title,
                "file_path": document.file_path,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "file_hash": document.file_hash,
                "status": document.status,
                "chunk_count": document.chunk_count,
                "text_length": document.text_length,
                "page_count": document.page_count,
                "created_at": document.created_at.isoformat() if document.created_at else None,
                "processed_at": document.processed_at.isoformat() if document.processed_at else None,
                "error_message": document.error_message
            }

        except Exception as e:
            self.logger.error(f"Failed to get document {document_id}: {e}")
            return None

    def list_documents(
        self,
        user_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List documents for a user"""
        try:
            documents = db_service.list_documents(
                user_id=user_id,
                status=status,
                skip=skip,
                limit=limit
            )

            return [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "status": doc.status,
                    "chunk_count": doc.chunk_count,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None
                }
                for doc in documents
            ]

        except Exception as e:
            self.logger.error(f"Failed to list documents: {e}")
            return []

    async def delete_document(self, document_id: int) -> bool:
        """Delete document and all associated data"""
        try:
            self.logger.info(f"🗑️ Deleting document: {document_id}")

            # Get document info
            document = db_service.get_document(document_id)
            if not document:
                self.logger.warning(f"Document not found: {document_id}")
                return False

            # Delete vectors from vector store
            vector_count = self.vector_service.delete_by_document(document_id)
            self.logger.info(f"Deleted {vector_count} vectors")

            # Delete file from storage
            try:
                if os.path.exists(document.file_path):
                    os.remove(document.file_path)
                    self.logger.info(f"Deleted file: {document.file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to delete file: {e}")

            # Delete from database (cascades to chunks)
            success = db_service.delete_document(document_id)

            if success:
                self.logger.info(f"✅ Document deleted: {document_id}")

            return success

        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {e}")
            return False

    def get_document_stats(self, document_id: int) -> Dict[str, Any]:
        """Get detailed statistics for a document"""
        try:
            return db_service.get_document_stats(document_id)
        except Exception as e:
            self.logger.error(f"Failed to get document stats: {e}")
            return {}


# Global document manager instance
document_manager = DocumentManager()


def get_document_manager() -> DocumentManager:
    """Get the global document manager instance"""
    return document_manager
