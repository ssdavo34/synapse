"""
Conversation Agent for SynapseSimple v2.0

Handles conversational interactions with context and memory management
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI

from config import settings
from prompts.templates import SystemPrompt, ConversationPrompt, RAGPrompt
from utils.logger import setup_logger


class Message:
    """Conversation message"""

    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize message

        Args:
            role: Message role (system, user, assistant)
            content: Message content
            timestamp: Message timestamp
            metadata: Additional metadata
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

    def to_openai_format(self) -> Dict[str, str]:
        """Convert to OpenAI API format"""
        return {
            "role": self.role,
            "content": self.content
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return Message(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )


class ConversationAgent:
    """
    Conversation agent with context management

    Handles:
    - Message history management
    - Context-aware responses
    - RAG integration
    - Token management
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        max_history_messages: int = 20
    ):
        """
        Initialize conversation agent

        Args:
            model: OpenAI model name
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            max_history_messages: Maximum messages to keep in history
        """
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_history_messages = max_history_messages
        self.logger = setup_logger(__name__)

        # Conversation history
        self.messages: List[Message] = []

        # System prompt
        self.system_message = Message(
            role="system",
            content=SystemPrompt.create_default()
        )

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Add message to conversation history

        Args:
            role: Message role (user, assistant)
            content: Message content
            metadata: Additional metadata

        Returns:
            Created message
        """
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)

        # Trim history if too long
        if len(self.messages) > self.max_history_messages:
            self.messages = self.messages[-self.max_history_messages:]

        return message

    def get_history(self, limit: Optional[int] = None) -> List[Message]:
        """
        Get conversation history

        Args:
            limit: Maximum messages to return

        Returns:
            List of messages
        """
        if limit:
            return self.messages[-limit:]
        return self.messages

    def format_history(self, limit: Optional[int] = None) -> str:
        """
        Format conversation history as text

        Args:
            limit: Maximum messages to include

        Returns:
            Formatted history string
        """
        messages = self.get_history(limit)

        if not messages:
            return "No conversation history."

        formatted = []
        for msg in messages:
            timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            formatted.append(f"[{timestamp}] {msg.role.upper()}: {msg.content}")

        return "\n".join(formatted)

    def clear_history(self):
        """Clear conversation history"""
        self.messages = []
        self.logger.info("Conversation history cleared")

    def _build_messages(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Build messages for OpenAI API

        Args:
            include_system: Whether to include system message

        Returns:
            List of message dictionaries
        """
        messages = []

        if include_system:
            messages.append(self.system_message.to_openai_format())

        for msg in self.messages:
            messages.append(msg.to_openai_format())

        return messages

    def chat(
        self,
        user_message: str,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message and get response

        Args:
            user_message: User's message
            context: Optional RAG context
            metadata: Additional metadata

        Returns:
            Response dictionary with content and metadata
        """
        try:
            # Add user message to history
            self.add_message("user", user_message, metadata)

            # Build messages for API
            messages = self._build_messages()

            # If context provided, modify the last user message to include context
            if context:
                rag_prompt = RAGPrompt.create_with_context(
                    query=user_message,
                    context=context
                )
                # Replace last message with RAG-enhanced version
                messages[-1] = {
                    "role": "user",
                    "content": rag_prompt
                }

            # Call OpenAI API
            self.logger.info(f"Sending chat request: {len(messages)} messages")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Extract response
            assistant_message = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason

            # Add assistant response to history
            self.add_message(
                "assistant",
                assistant_message,
                metadata={
                    "finish_reason": finish_reason,
                    "model": self.model,
                    "has_context": context is not None
                }
            )

            # Build response
            result = {
                "success": True,
                "content": assistant_message,
                "finish_reason": finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "metadata": {
                    "model": self.model,
                    "has_context": context is not None,
                    "message_count": len(self.messages)
                }
            }

            self.logger.info(
                f"Chat response received: {response.usage.total_tokens} tokens, "
                f"finish_reason={finish_reason}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Chat error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "content": "I apologize, but I encountered an error processing your request.",
                "metadata": {}
            }

    def chat_with_rag(
        self,
        user_message: str,
        context: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Chat with RAG context (convenience method)

        Args:
            user_message: User's message
            context: RAG context from document search
            metadata: Additional metadata

        Returns:
            Response dictionary
        """
        return self.chat(user_message, context=context, metadata=metadata)

    def set_system_prompt(self, prompt: str):
        """
        Set custom system prompt

        Args:
            prompt: New system prompt
        """
        self.system_message = Message(role="system", content=prompt)
        self.logger.info("System prompt updated")

    def get_conversation_summary(self) -> str:
        """
        Get a summary of the current conversation

        Returns:
            Summary string
        """
        if not self.messages:
            return "No conversation yet."

        user_messages = [msg for msg in self.messages if msg.role == "user"]
        assistant_messages = [msg for msg in self.messages if msg.role == "assistant"]

        summary = f"Conversation Summary:\n"
        summary += f"- Total messages: {len(self.messages)}\n"
        summary += f"- User messages: {len(user_messages)}\n"
        summary += f"- Assistant messages: {len(assistant_messages)}\n"

        if self.messages:
            first_msg = self.messages[0]
            last_msg = self.messages[-1]
            summary += f"- Started: {first_msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            summary += f"- Last activity: {last_msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"

        return summary

    def export_conversation(self) -> List[Dict[str, Any]]:
        """
        Export conversation to dictionary format

        Returns:
            List of message dictionaries
        """
        return [msg.to_dict() for msg in self.messages]

    def import_conversation(self, messages: List[Dict[str, Any]]):
        """
        Import conversation from dictionary format

        Args:
            messages: List of message dictionaries
        """
        self.messages = [Message.from_dict(msg) for msg in messages]
        self.logger.info(f"Imported {len(messages)} messages")

    def get_token_estimate(self) -> int:
        """
        Estimate tokens in current conversation

        Returns:
            Estimated token count (rough approximation)
        """
        # Rough estimate: 1 token ≈ 4 characters
        total_chars = sum(len(msg.content) for msg in self.messages)
        total_chars += len(self.system_message.content)
        return total_chars // 4

    def should_summarize(self, token_threshold: int = 3000) -> bool:
        """
        Check if conversation should be summarized

        Args:
            token_threshold: Token threshold for summarization

        Returns:
            Whether summarization is recommended
        """
        return self.get_token_estimate() > token_threshold
