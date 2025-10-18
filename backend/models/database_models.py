"""
Database Models for SynapseSimple v2.0

SQLAlchemy 2.0 ORM models with SQLite compatibility
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Integer, String, Text, DateTime, Boolean, ForeignKey,
    create_engine, Column
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class User(Base):
    """User model"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    chats: Mapped[List["Chat"]] = relationship("Chat", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"


class Document(Base):
    """Document model"""
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    # File hash for duplicate detection (SHA-256)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)

    # Processing status: pending, processing, completed, failed
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)

    # Extracted text
    full_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Metadata
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="documents")
    chunks: Mapped[List["Chunk"]] = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title='{self.title}', status='{self.status}')>"


class Chunk(Base):
    """Text chunk model"""
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)

    # Chunk content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # Token and character counts
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Embedding metadata
    has_embedding: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vector_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<Chunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index}, tokens={self.token_count})>"


class Chat(Base):
    """Chat session model"""
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Chat metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    session_type: Mapped[str] = mapped_column(String(50), nullable=False)  # rag, quiz, planning, etc.

    # Status: active, archived, deleted
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    # Associated document (optional)
    document_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)

    # Message count
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chats")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, title='{self.title}', type='{self.session_type}')>"


class Message(Base):
    """Chat message model"""
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)

    # Message content
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Token count
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Context metadata (for RAG)
    context_chunks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string of chunk IDs

    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, chat_id={self.chat_id}, role='{self.role}')>"


# Indexes for performance
from sqlalchemy import Index

# Document indexes
Index('idx_documents_user_status', Document.user_id, Document.status)
Index('idx_documents_created', Document.created_at.desc())

# Chunk indexes
Index('idx_chunks_document', Chunk.document_id, Chunk.chunk_index)
Index('idx_chunks_vector', Chunk.vector_id)

# Chat indexes
Index('idx_chats_user_status', Chat.user_id, Chat.status)
Index('idx_chats_updated', Chat.updated_at.desc())

# Message indexes
Index('idx_messages_chat_timestamp', Message.chat_id, Message.timestamp)
