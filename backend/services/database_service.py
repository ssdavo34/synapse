"""
Database Service for SynapseSimple v2.0

SQLAlchemy 2.0 with SQLite backend
Provides database session management and CRUD operations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Optional, List, Generator
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import create_engine, select, update, delete, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from config import settings
from utils.logger import setup_logger
from models.database_models import Base, User, Document, Chunk, Chat, Message


class DatabaseService:
    """Database service with connection pooling and CRUD operations"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.database_url = settings.database_url

        # Create engine with SQLite-specific settings
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
            echo=settings.debug_mode
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        self.logger.info(f"Database service initialized: {self.database_url}")

    def init_db(self) -> None:
        """Initialize database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("✅ Database tables created successfully")
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Failed to create tables: {e}")
            raise

    def drop_all_tables(self) -> None:
        """Drop all tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            self.logger.warning("⚠️ All tables dropped")
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Failed to drop tables: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_db(self) -> Generator[Session, None, None]:
        """Dependency injection for FastAPI"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    # ==================== User CRUD ====================

    def create_user(self, email: str, name: str) -> User:
        """Create a new user"""
        with self.get_session() as session:
            user = User(email=email, name=name)
            session.add(user)
            session.commit()
            session.refresh(user)
            user_id = user.id  # Extract ID before session closes
            self.logger.info(f"User created: {user_id} - {email}")

            # Make object usable outside session
            session.expunge(user)
            return user

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        with self.get_session() as session:
            stmt = select(User).where(User.id == user_id)
            return session.scalar(stmt)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        with self.get_session() as session:
            stmt = select(User).where(User.email == email)
            return session.scalar(stmt)

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users"""
        with self.get_session() as session:
            stmt = select(User).offset(skip).limit(limit)
            return list(session.scalars(stmt))

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields"""
        with self.get_session() as session:
            stmt = update(User).where(User.id == user_id).values(**kwargs)
            session.execute(stmt)
            return self.get_user(user_id)

    def delete_user(self, user_id: int) -> bool:
        """Delete user (cascades to documents and chats)"""
        with self.get_session() as session:
            stmt = delete(User).where(User.id == user_id)
            result = session.execute(stmt)
            success = result.rowcount > 0
            if success:
                self.logger.info(f"User deleted: {user_id}")
            return success

    # ==================== Document CRUD ====================

    def create_document(
        self,
        user_id: int,
        title: str,
        file_path: str,
        file_type: str,
        file_size: int,
        file_hash: Optional[str] = None
    ) -> Document:
        """Create a new document"""
        with self.get_session() as session:
            document = Document(
                user_id=user_id,
                title=title,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                file_hash=file_hash,
                status="pending"
            )
            session.add(document)
            session.flush()
            session.refresh(document)
            self.logger.info(f"Document created: {document.id} - {title}")
            return document

    def get_document(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        with self.get_session() as session:
            stmt = select(Document).where(Document.id == document_id)
            return session.scalar(stmt)

    def get_document_by_hash(self, file_hash: str, user_id: Optional[int] = None) -> Optional[Document]:
        """Get document by file hash (for duplicate detection)"""
        with self.get_session() as session:
            stmt = select(Document).where(Document.file_hash == file_hash)
            if user_id:
                stmt = stmt.where(Document.user_id == user_id)
            return session.scalar(stmt)

    def list_documents(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """List documents with optional filters"""
        with self.get_session() as session:
            stmt = select(Document)

            if user_id:
                stmt = stmt.where(Document.user_id == user_id)
            if status:
                stmt = stmt.where(Document.status == status)

            stmt = stmt.order_by(Document.created_at.desc()).offset(skip).limit(limit)
            return list(session.scalars(stmt))

    def update_document(self, document_id: int, **kwargs) -> Optional[Document]:
        """Update document fields"""
        with self.get_session() as session:
            if "status" in kwargs and kwargs["status"] == "completed":
                kwargs["processed_at"] = datetime.utcnow()

            stmt = update(Document).where(Document.id == document_id).values(**kwargs)
            session.execute(stmt)
            return self.get_document(document_id)

    def delete_document(self, document_id: int) -> bool:
        """Delete document (cascades to chunks)"""
        with self.get_session() as session:
            stmt = delete(Document).where(Document.id == document_id)
            result = session.execute(stmt)
            success = result.rowcount > 0
            if success:
                self.logger.info(f"Document deleted: {document_id}")
            return success

    # ==================== Chunk CRUD ====================

    def create_chunk(
        self,
        document_id: int,
        content: str,
        chunk_index: int,
        token_count: int,
        char_count: int
    ) -> Chunk:
        """Create a new chunk"""
        with self.get_session() as session:
            chunk = Chunk(
                document_id=document_id,
                content=content,
                chunk_index=chunk_index,
                token_count=token_count,
                char_count=char_count
            )
            session.add(chunk)
            session.flush()
            session.refresh(chunk)
            return chunk

    def create_chunks_bulk(self, chunks_data: List[dict]) -> List[Chunk]:
        """Bulk create chunks for efficiency"""
        with self.get_session() as session:
            chunks = [Chunk(**data) for data in chunks_data]
            session.add_all(chunks)
            session.flush()
            for chunk in chunks:
                session.refresh(chunk)
            self.logger.info(f"Bulk created {len(chunks)} chunks")
            return chunks

    def get_chunk(self, chunk_id: int) -> Optional[Chunk]:
        """Get chunk by ID"""
        with self.get_session() as session:
            stmt = select(Chunk).where(Chunk.id == chunk_id)
            return session.scalar(stmt)

    def get_chunks_by_ids(self, chunk_ids: List[int]) -> List[Chunk]:
        """Get multiple chunks by IDs"""
        with self.get_session() as session:
            stmt = select(Chunk).where(Chunk.id.in_(chunk_ids))
            return list(session.scalars(stmt))

    def list_chunks(self, document_id: int) -> List[Chunk]:
        """List all chunks for a document"""
        with self.get_session() as session:
            stmt = select(Chunk).where(
                Chunk.document_id == document_id
            ).order_by(Chunk.chunk_index)
            return list(session.scalars(stmt))

    def update_chunk(self, chunk_id: int, **kwargs) -> Optional[Chunk]:
        """Update chunk fields"""
        with self.get_session() as session:
            stmt = update(Chunk).where(Chunk.id == chunk_id).values(**kwargs)
            session.execute(stmt)
            return self.get_chunk(chunk_id)

    def delete_chunks_by_document(self, document_id: int) -> int:
        """Delete all chunks for a document"""
        with self.get_session() as session:
            stmt = delete(Chunk).where(Chunk.document_id == document_id)
            result = session.execute(stmt)
            count = result.rowcount
            self.logger.info(f"Deleted {count} chunks for document {document_id}")
            return count

    # ==================== Chat CRUD ====================

    def create_chat(
        self,
        user_id: int,
        title: str,
        session_type: str,
        document_id: Optional[int] = None
    ) -> Chat:
        """Create a new chat session"""
        with self.get_session() as session:
            chat = Chat(
                user_id=user_id,
                title=title,
                session_type=session_type,
                document_id=document_id
            )
            session.add(chat)
            session.commit()
            session.refresh(chat)
            chat_id = chat.id  # Extract ID before session closes
            self.logger.info(f"Chat created: {chat_id} - {title}")

            # Make object usable outside session
            session.expunge(chat)
            return chat

    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Get chat by ID"""
        with self.get_session() as session:
            stmt = select(Chat).where(Chat.id == chat_id)
            chat = session.scalar(stmt)
            if chat:
                session.expunge(chat)
            return chat

    def list_chats(
        self,
        user_id: int,
        status: str = "active",
        skip: int = 0,
        limit: int = 100
    ) -> List[Chat]:
        """List chats for a user"""
        with self.get_session() as session:
            stmt = select(Chat).where(
                Chat.user_id == user_id,
                Chat.status == status
            ).order_by(Chat.updated_at.desc()).offset(skip).limit(limit)
            chats = list(session.scalars(stmt))
            # Expunge all chats to make them usable outside session
            for chat in chats:
                session.expunge(chat)
            return chats

    def get_user_chats(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Chat]:
        """Get user's chats (alias for list_chats)"""
        return self.list_chats(user_id, skip=offset, limit=limit)

    def update_chat(self, chat_id: int, **kwargs) -> Optional[Chat]:
        """Update chat fields"""
        with self.get_session() as session:
            stmt = update(Chat).where(Chat.id == chat_id).values(**kwargs)
            session.execute(stmt)
            return self.get_chat(chat_id)

    def delete_chat(self, chat_id: int) -> bool:
        """Delete chat (cascades to messages)"""
        with self.get_session() as session:
            stmt = delete(Chat).where(Chat.id == chat_id)
            result = session.execute(stmt)
            success = result.rowcount > 0
            if success:
                self.logger.info(f"Chat deleted: {chat_id}")
            return success

    # ==================== Message CRUD ====================

    def create_message(
        self,
        chat_id: int,
        role: str,
        content: str,
        token_count: Optional[int] = None,
        context_chunks: Optional[str] = None
    ) -> Message:
        """Create a new message"""
        with self.get_session() as session:
            message = Message(
                chat_id=chat_id,
                role=role,
                content=content,
                token_count=token_count,
                context_chunks=context_chunks
            )
            session.add(message)
            session.flush()
            session.refresh(message)

            # Update chat metadata
            stmt_update = update(Chat).where(Chat.id == chat_id).values(
                message_count=Chat.message_count + 1,
                last_message_at=datetime.utcnow()
            )
            session.execute(stmt_update)

            return message

    def get_message(self, message_id: int) -> Optional[Message]:
        """Get message by ID"""
        with self.get_session() as session:
            stmt = select(Message).where(Message.id == message_id)
            return session.scalar(stmt)

    def list_messages(
        self,
        chat_id: int,
        limit: Optional[int] = None
    ) -> List[Message]:
        """List messages for a chat"""
        with self.get_session() as session:
            stmt = select(Message).where(
                Message.chat_id == chat_id
            ).order_by(Message.timestamp)

            if limit:
                stmt = stmt.limit(limit)

            messages = list(session.scalars(stmt))
            # Expunge all messages to make them usable outside session
            for message in messages:
                session.expunge(message)
            return messages

    def get_chat_messages(
        self,
        chat_id: int,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Message]:
        """Get chat messages (alias for list_messages)"""
        # Note: offset not implemented in list_messages, just use limit
        return self.list_messages(chat_id, limit=limit)

    def get_recent_messages(self, chat_id: int, limit: int = 10) -> List[Message]:
        """Get recent messages for context"""
        with self.get_session() as session:
            stmt = select(Message).where(
                Message.chat_id == chat_id
            ).order_by(Message.timestamp.desc()).limit(limit)

            messages = list(session.scalars(stmt))
            return list(reversed(messages))  # Return in chronological order

    # ==================== Statistics ====================

    def get_user_stats(self, user_id: int) -> dict:
        """Get statistics for a user"""
        with self.get_session() as session:
            document_count = session.scalar(
                select(func.count(Document.id)).where(Document.user_id == user_id)
            )
            chat_count = session.scalar(
                select(func.count(Chat.id)).where(Chat.user_id == user_id)
            )

            return {
                "user_id": user_id,
                "document_count": document_count or 0,
                "chat_count": chat_count or 0
            }

    def get_document_stats(self, document_id: int) -> dict:
        """Get statistics for a document"""
        document = self.get_document(document_id)
        if not document:
            return {}

        return {
            "document_id": document_id,
            "title": document.title,
            "status": document.status,
            "chunk_count": document.chunk_count,
            "text_length": document.text_length,
            "page_count": document.page_count,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "processed_at": document.processed_at.isoformat() if document.processed_at else None
        }


# Global database service instance
db_service = DatabaseService()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions"""
    return db_service.get_db()


def init_database() -> None:
    """Initialize database (create tables)"""
    db_service.init_db()
