"""
Day 3 Manual Integration Test

Simple test script to verify Day 3 implementation
Run from backend directory: python test_day3_manual.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from config import settings, ensure_directories
from services.database_service import db_service
from services.vector_store import vector_store
from utils.logger import setup_logger


async def test_day3_integration():
    """Test Day 3 components"""
    logger = setup_logger(__name__)

    print("\n" + "="*60)
    print("Day 3 Integration Test")
    print("="*60 + "\n")

    # Test 1: Config
    print("Test 1: Configuration")
    print(f"  DATABASE_URL: {settings.database_url}")
    print(f"  QDRANT_PATH: {settings.qdrant_path}")
    print(f"  UPLOAD_DIR: {settings.upload_dir}")
    print("  ✅ Config loaded\n")

    # Test 2: Directory creation
    print("Test 2: Ensure directories")
    ensure_directories()
    print("  ✅ Directories created\n")

    # Test 3: Database initialization
    print("Test 3: Database initialization")
    try:
        db_service.init_db()
        print("  ✅ Database tables created\n")
    except Exception as e:
        print(f"  ❌ Database init failed: {e}\n")
        return

    # Test 4: Vector store initialization
    print("Test 4: Vector store initialization")
    try:
        info = vector_store.get_collection_info()
        print(f"  Collection: {info.get('name')}")
        print(f"  Vector size: {info.get('vector_size')}")
        print(f"  Points count: {info.get('points_count')}")
        print("  ✅ Vector store initialized\n")
    except Exception as e:
        print(f"  ❌ Vector store failed: {e}\n")
        return

    # Test 5: User CRUD
    print("Test 5: User CRUD")
    try:
        # Create user
        user = db_service.create_user(
            email="test@example.com",
            name="Test User"
        )
        print(f"  Created user: ID={user.id}, email={user.email}")

        # Get user
        retrieved = db_service.get_user(user.id)
        assert retrieved.id == user.id
        print(f"  Retrieved user: {retrieved.name}")

        # List users
        users = db_service.list_users()
        print(f"  Total users: {len(users)}")
        print("  ✅ User CRUD working\n")
    except Exception as e:
        print(f"  ❌ User CRUD failed: {e}\n")
        return

    # Test 6: Document CRUD
    print("Test 6: Document CRUD")
    try:
        # Create document
        doc = db_service.create_document(
            user_id=user.id,
            title="Test Document",
            file_path="/fake/path/test.pdf",
            file_type="application/pdf",
            file_size=1024,
            file_hash="abc123"
        )
        print(f"  Created document: ID={doc.id}, title={doc.title}")

        # Update document
        db_service.update_document(doc.id, status="completed")
        updated = db_service.get_document(doc.id)
        assert updated.status == "completed"
        print(f"  Updated status: {updated.status}")
        print("  ✅ Document CRUD working\n")
    except Exception as e:
        print(f"  ❌ Document CRUD failed: {e}\n")
        return

    # Test 7: Chunk CRUD
    print("Test 7: Chunk CRUD")
    try:
        # Create chunk
        chunk = db_service.create_chunk(
            document_id=doc.id,
            content="This is a test chunk content.",
            chunk_index=0,
            token_count=10,
            char_count=30
        )
        print(f"  Created chunk: ID={chunk.id}, tokens={chunk.token_count}")

        # List chunks
        chunks = db_service.list_chunks(doc.id)
        print(f"  Chunks for document: {len(chunks)}")
        print("  ✅ Chunk CRUD working\n")
    except Exception as e:
        print(f"  ❌ Chunk CRUD failed: {e}\n")
        return

    # Test 8: Vector operations
    print("Test 8: Vector operations")
    try:
        # Upsert test vector
        test_vector = [0.1] * 1536  # Dummy 1536-dim vector
        success = vector_store.upsert_point(
            point_id="test_chunk_1",
            vector=test_vector,
            payload={
                "chunk_id": chunk.id,
                "document_id": doc.id,
                "content": chunk.content
            }
        )
        print(f"  Upserted vector: {success}")

        # Count points
        count = vector_store.count_points()
        print(f"  Total vectors: {count}")
        print("  ✅ Vector operations working\n")
    except Exception as e:
        print(f"  ❌ Vector operations failed: {e}\n")
        return

    # Test 9: Chat & Message CRUD
    print("Test 9: Chat & Message CRUD")
    try:
        # Create chat
        chat = db_service.create_chat(
            user_id=user.id,
            title="Test Chat",
            session_type="rag",
            document_id=doc.id
        )
        print(f"  Created chat: ID={chat.id}, type={chat.session_type}")

        # Create message
        message = db_service.create_message(
            chat_id=chat.id,
            role="user",
            content="Hello, this is a test message"
        )
        print(f"  Created message: ID={message.id}, role={message.role}")

        # Get messages
        messages = db_service.list_messages(chat.id)
        print(f"  Messages in chat: {len(messages)}")
        print("  ✅ Chat & Message CRUD working\n")
    except Exception as e:
        print(f"  ❌ Chat & Message CRUD failed: {e}\n")
        return

    # Test 10: Statistics
    print("Test 10: Statistics")
    try:
        stats = db_service.get_user_stats(user.id)
        print(f"  User stats: {stats}")

        doc_stats = db_service.get_document_stats(doc.id)
        print(f"  Document stats: chunk_count={doc_stats.get('chunk_count')}")
        print("  ✅ Statistics working\n")
    except Exception as e:
        print(f"  ❌ Statistics failed: {e}\n")

    print("="*60)
    print("✅ All Day 3 tests passed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_day3_integration())
