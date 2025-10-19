"""
Chat Manager for SynapseSimple v2.0

High-level chat management with database persistence and RAG integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Any, Optional
from datetime import datetime

from agents.rag_pipeline import RAGPipeline
from agents.conversation_agent import ConversationAgent
from services.database_service import DatabaseService
from models.database_models import Chat, Message as DBMessage
from utils.logger import setup_logger


class ChatManager:
    """
    Chat manager with persistence and RAG

    Features:
    - Create and manage chat sessions
    - Persist messages to database
    - Integrate RAG for document-based Q&A
    - Load/save conversation history
    - Multiple chat sessions per user
    """

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        rag_pipeline: Optional[RAGPipeline] = None
    ):
        """
        Initialize chat manager

        Args:
            db_service: Database service instance
            rag_pipeline: RAG pipeline instance
        """
        self.db_service = db_service or DatabaseService()
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self.logger = setup_logger(__name__)

        # Cache for active chat sessions
        self._chat_cache: Dict[int, ConversationAgent] = {}

        self.logger.info("Chat Manager initialized")

    def create_chat(
        self,
        user_id: int,
        title: Optional[str] = None,
        session_type: str = "general",
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create new chat session

        Args:
            user_id: User ID
            title: Chat title (optional, auto-generated if not provided)
            session_type: Session type (general, rag, quiz, etc.)
            document_id: Associated document ID (optional)

        Returns:
            Chat info dictionary
        """
        try:
            # Generate title if not provided
            if not title:
                title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            # Create chat in database
            chat = self.db_service.create_chat(
                user_id=user_id,
                title=title,
                session_type=session_type,
                document_id=document_id
            )

            chat_id = chat.id

            self.logger.info(f"Chat created: chat_id={chat_id}, user_id={user_id}")

            return {
                "success": True,
                "chat_id": chat_id,
                "user_id": user_id,
                "title": title,
                "created_at": chat.created_at.isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to create chat: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """
        Get chat by ID

        Args:
            chat_id: Chat ID

        Returns:
            Chat object or None
        """
        return self.db_service.get_chat(chat_id)

    def get_user_chats(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Chat]:
        """
        Get user's chat sessions

        Args:
            user_id: User ID
            limit: Maximum chats to return
            offset: Offset for pagination

        Returns:
            List of Chat objects
        """
        return self.db_service.get_user_chats(user_id, limit, offset)

    def delete_chat(self, chat_id: int) -> bool:
        """
        Delete chat session

        Args:
            chat_id: Chat ID

        Returns:
            Success status
        """
        try:
            # Remove from cache if exists
            if chat_id in self._chat_cache:
                del self._chat_cache[chat_id]

            # Delete from database
            success = self.db_service.delete_chat(chat_id)

            if success:
                self.logger.info(f"Chat deleted: chat_id={chat_id}")

            return success

        except Exception as e:
            self.logger.error(f"Failed to delete chat: {e}", exc_info=True)
            return False

    def _get_or_create_agent(self, chat_id: int) -> ConversationAgent:
        """
        Get cached agent or create new one

        Args:
            chat_id: Chat ID

        Returns:
            ConversationAgent instance
        """
        if chat_id not in self._chat_cache:
            # Create new agent
            agent = ConversationAgent()

            # Load message history from database
            messages = self.db_service.get_chat_messages(chat_id)

            # Import messages to agent (excluding system messages)
            for msg in messages:
                if msg.role != "system":
                    agent.add_message(
                        role=msg.role,
                        content=msg.content,
                        metadata=msg.metadata
                    )

            self._chat_cache[chat_id] = agent

        return self._chat_cache[chat_id]

    def send_message(
        self,
        chat_id: int,
        user_message: str,
        use_rag: bool = False,
        user_id: Optional[int] = None,
        document_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message in chat session

        Args:
            chat_id: Chat ID
            user_message: User's message
            use_rag: Whether to use RAG for document context
            user_id: User ID for RAG filtering
            document_id: Document ID for RAG filtering
            metadata: Additional metadata

        Returns:
            Response dictionary
        """
        try:
            # Verify chat exists
            chat = self.get_chat(chat_id)
            if not chat:
                return {
                    "success": False,
                    "error": f"Chat {chat_id} not found"
                }

            # Save user message to database
            user_msg_db = self.db_service.create_message(
                chat_id=chat_id,
                role="user",
                content=user_message,
                metadata=metadata
            )

            # Get response
            if use_rag:
                # Use RAG pipeline
                rag_result = self.rag_pipeline.query(
                    question=user_message,
                    user_id=user_id,
                    document_id=document_id,
                    metadata=metadata
                )

                if not rag_result.get("success"):
                    return rag_result

                assistant_message = rag_result["answer"]
                response_metadata = {
                    "rag_enabled": True,
                    "sources": rag_result.get("sources", []),
                    "has_context": rag_result.get("has_context", False),
                    "search_results_count": rag_result.get("search_results_count", 0),
                    "usage": rag_result.get("usage", {})
                }

            else:
                # Use conversation agent directly
                agent = self._get_or_create_agent(chat_id)
                agent_result = agent.chat(user_message, metadata=metadata)

                if not agent_result.get("success"):
                    return agent_result

                assistant_message = agent_result["content"]
                response_metadata = {
                    "rag_enabled": False,
                    "usage": agent_result.get("usage", {})
                }

            # Save assistant message to database
            assistant_msg_db = self.db_service.create_message(
                chat_id=chat_id,
                role="assistant",
                content=assistant_message,
                metadata=response_metadata
            )

            # Update chat's last activity
            self.db_service.update_chat(
                chat_id=chat_id,
                updated_at=datetime.now()
            )

            self.logger.info(
                f"Message sent: chat_id={chat_id}, "
                f"use_rag={use_rag}, "
                f"response_length={len(assistant_message)}"
            )

            return {
                "success": True,
                "chat_id": chat_id,
                "user_message_id": user_msg_db.id,
                "assistant_message_id": assistant_msg_db.id,
                "user_message": user_message,
                "assistant_message": assistant_message,
                "metadata": response_metadata
            }

        except Exception as e:
            self.logger.error(f"Failed to send message: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_chat_messages(
        self,
        chat_id: int,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[DBMessage]:
        """
        Get chat messages

        Args:
            chat_id: Chat ID
            limit: Maximum messages to return
            offset: Offset for pagination

        Returns:
            List of Message objects
        """
        return self.db_service.get_chat_messages(chat_id, limit, offset)

    def format_chat_history(
        self,
        chat_id: int,
        limit: Optional[int] = None
    ) -> str:
        """
        Format chat history as readable text

        Args:
            chat_id: Chat ID
            limit: Maximum messages to include

        Returns:
            Formatted history string
        """
        messages = self.get_chat_messages(chat_id, limit)

        if not messages:
            return "No messages in this chat."

        formatted = []
        for msg in messages:
            if msg.role == "system":
                continue

            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            role = msg.role.upper()
            formatted.append(f"[{timestamp}] {role}: {msg.content}")

        return "\n".join(formatted)

    def export_chat(self, chat_id: int) -> Dict[str, Any]:
        """
        Export chat with all messages

        Args:
            chat_id: Chat ID

        Returns:
            Chat export dictionary
        """
        chat = self.get_chat(chat_id)
        if not chat:
            return {
                "success": False,
                "error": f"Chat {chat_id} not found"
            }

        messages = self.get_chat_messages(chat_id)

        return {
            "success": True,
            "chat": {
                "id": chat.id,
                "user_id": chat.user_id,
                "title": chat.title,
                "created_at": chat.created_at.isoformat(),
                "updated_at": chat.updated_at.isoformat(),
                "metadata": chat.metadata
            },
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in messages
            ]
        }

    def update_chat_title(self, chat_id: int, title: str) -> bool:
        """
        Update chat title

        Args:
            chat_id: Chat ID
            title: New title

        Returns:
            Success status
        """
        try:
            self.db_service.update_chat(chat_id=chat_id, title=title)
            self.logger.info(f"Chat title updated: chat_id={chat_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update chat title: {e}", exc_info=True)
            return False

    def clear_chat_cache(self, chat_id: Optional[int] = None):
        """
        Clear cached agents

        Args:
            chat_id: Specific chat ID to clear, or None for all
        """
        if chat_id:
            if chat_id in self._chat_cache:
                del self._chat_cache[chat_id]
                self.logger.info(f"Chat cache cleared: chat_id={chat_id}")
        else:
            self._chat_cache.clear()
            self.logger.info("All chat cache cleared")

    def get_chat_statistics(self, chat_id: int) -> Dict[str, Any]:
        """
        Get chat statistics

        Args:
            chat_id: Chat ID

        Returns:
            Statistics dictionary
        """
        messages = self.get_chat_messages(chat_id)

        user_messages = [msg for msg in messages if msg.role == "user"]
        assistant_messages = [msg for msg in messages if msg.role == "assistant"]

        # Calculate total tokens from metadata
        total_tokens = 0
        for msg in messages:
            if msg.metadata and "usage" in msg.metadata:
                total_tokens += msg.metadata["usage"].get("total_tokens", 0)

        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_tokens": total_tokens,
            "average_tokens_per_message": total_tokens // len(messages) if messages else 0
        }


# Global chat manager instance
chat_manager = ChatManager()


def get_chat_manager() -> ChatManager:
    """Get the global chat manager instance"""
    return chat_manager
