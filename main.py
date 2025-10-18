"""
SynapseSimple - Minimal FastAPI Project
Phase 5: File Upload with Storage, PDF Text Extraction, Chunking, Embeddings, and ChromaDB
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
import os
from datetime import datetime
import fitz  # pymupdf
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
import uuid

# .env 파일 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ChromaDB 클라이언트 초기화
chroma_client = chromadb.PersistentClient(path="data/vector_db")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="SynapseSimple",
    description="Minimal FastAPI for file upload",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작"""
    logger.info("=" * 50)
    logger.info("🚀 SynapseSimple Starting...")
    logger.info("=" * 50)


@app.get("/api/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    logger.info("💚 Health check called")
    return {
        "status": "healthy",
        "message": "SynapseSimple is running"
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    파일 업로드 엔드포인트
    Phase 5: 파일 저장, 텍스트 추출, 청킹, 임베딩 생성, ChromaDB 저장
    """
    try:
        logger.info("=" * 50)
        logger.info("📤 Upload request received")
        logger.info(f"📁 Filename: {file.filename}")
        logger.info(f"📊 Content-Type: {file.content_type}")

        # 파일 크기 확인
        content = await file.read()
        file_size = len(content)
        logger.info(f"📏 File size: {file_size} bytes")

        # 저장 폴더 생성
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"📂 Upload directory: {upload_dir}")

        # 타임스탬프 추가한 파일명
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        logger.info(f"💾 Saving to: {file_path}")

        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"✅ File saved successfully: {file_path}")

        # Phase 2: PDF 텍스트 추출
        logger.info("📖 Extracting text from PDF...")

        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        text_length = len(text)
        logger.info(f"✅ Extracted {text_length} characters from PDF")
        logger.info(f"📄 Text preview: {text[:100]}...")

        # Phase 3: 텍스트 청킹
        logger.info("✂️ Chunking text...")

        chunk_size = 500
        overlap = 50
        chunks = []

        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size].strip()
            if chunk:  # 빈 청크 제외
                chunks.append(chunk)

        chunks_count = len(chunks)
        logger.info(f"✅ Created {chunks_count} chunks")
        logger.info(f"📦 Chunk size: {chunk_size}, Overlap: {overlap}")

        # Phase 4: 임베딩 생성
        logger.info("🔢 Generating embeddings...")

        embeddings = []
        for i, chunk in enumerate(chunks):
            response_embedding = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            )
            embedding = response_embedding.data[0].embedding
            embeddings.append(embedding)
            logger.info(f"  ✅ Chunk {i+1}/{len(chunks)} embedded")

        embedding_dim = len(embeddings[0]) if embeddings else 0
        logger.info(f"✅ Generated {len(embeddings)} embeddings (dim: {embedding_dim})")

        # Phase 5: ChromaDB 저장
        logger.info("💾 Saving to ChromaDB...")

        # 세션 ID 생성
        session_id = str(uuid.uuid4())
        collection_name = f"session_{session_id}"

        # 컬렉션 생성
        collection = chroma_client.create_collection(
            name=collection_name,
            metadata={"filename": file.filename}
        )

        # 데이터 저장
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[f"chunk_{i}" for i in range(len(chunks))],
            metadatas=[{"chunk_index": i} for i in range(len(chunks))]
        )

        logger.info(f"✅ Saved to ChromaDB: {collection_name}")
        logger.info(f"📊 Session ID: {session_id}")

        # 성공 응답
        response = {
            "status": "success",
            "message": "File uploaded, saved, text extracted, chunked, embedded, and stored in ChromaDB successfully",
            "filename": file.filename,
            "saved_filename": filename,
            "content_type": file.content_type,
            "size_bytes": file_size,
            "file_path": file_path,
            "extracted_text": text[:500],  # 처음 500자만
            "text_length": text_length,
            "text_preview": text[:200],  # 미리보기
            "chunks": chunks[:3],  # 처음 3개만 미리보기
            "chunks_count": chunks_count,
            "embeddings_count": len(embeddings),
            "embedding_dimension": embedding_dim,
            "session_id": session_id,
            "collection_name": collection_name
        }

        logger.info("✅ Upload successful")
        logger.info("=" * 50)

        return response

    except Exception as e:
        logger.error("=" * 50)
        logger.error("❌ Upload failed")
        logger.error(f"Error: {str(e)}", exc_info=True)
        logger.error("=" * 50)
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
