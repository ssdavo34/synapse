"""
Response Formatter for SynapseSimple v2.0

Format AI responses for different output types (text, JSON, markdown)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from utils.logger import setup_logger


class ResponseFormatter:
    """
    Format AI responses for different contexts

    Supports:
    - Plain text formatting
    - JSON formatting
    - Markdown formatting
    - Source citations
    - Metadata display
    """

    def __init__(self):
        self.logger = setup_logger(__name__)

    def format_text(
        self,
        content: str,
        include_sources: bool = False,
        sources: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format response as plain text

        Args:
            content: Main response content
            include_sources: Whether to include source citations
            sources: List of source dictionaries
            metadata: Additional metadata

        Returns:
            Formatted text string
        """
        output = content

        # Add sources if available
        if include_sources and sources:
            output += "\n\n" + self._format_sources_text(sources)

        # Add metadata if available
        if metadata and metadata.get("usage"):
            usage = metadata["usage"]
            output += f"\n\n[Tokens: {usage.get('total_tokens', 0)}]"

        return output

    def format_markdown(
        self,
        content: str,
        include_sources: bool = False,
        sources: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Format response as markdown

        Args:
            content: Main response content
            include_sources: Whether to include source citations
            sources: List of source dictionaries
            metadata: Additional metadata
            title: Optional title

        Returns:
            Formatted markdown string
        """
        output = []

        # Add title if provided
        if title:
            output.append(f"# {title}\n")

        # Add main content
        output.append(content)

        # Add sources section
        if include_sources and sources:
            output.append("\n## Sources\n")
            output.append(self._format_sources_markdown(sources))

        # Add metadata section
        if metadata:
            output.append("\n## Metadata\n")
            output.append(self._format_metadata_markdown(metadata))

        return "\n".join(output)

    def format_json(
        self,
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: str = "success"
    ) -> str:
        """
        Format response as JSON

        Args:
            content: Main response content
            sources: List of source dictionaries
            metadata: Additional metadata
            status: Response status

        Returns:
            JSON string
        """
        response = {
            "status": status,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        if sources:
            response["sources"] = sources

        if metadata:
            response["metadata"] = metadata

        return json.dumps(response, indent=2, ensure_ascii=False)

    def format_chat_message(
        self,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        include_timestamp: bool = True
    ) -> str:
        """
        Format single chat message

        Args:
            role: Message role (user, assistant)
            content: Message content
            timestamp: Message timestamp
            include_timestamp: Whether to include timestamp

        Returns:
            Formatted message string
        """
        timestamp = timestamp or datetime.now()

        if include_timestamp:
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            return f"[{time_str}] {role.upper()}: {content}"
        else:
            return f"{role.upper()}: {content}"

    def format_chat_history(
        self,
        messages: List[Dict[str, Any]],
        include_timestamps: bool = True,
        limit: Optional[int] = None
    ) -> str:
        """
        Format chat history

        Args:
            messages: List of message dictionaries
            include_timestamps: Whether to include timestamps
            limit: Maximum messages to format

        Returns:
            Formatted history string
        """
        if limit:
            messages = messages[-limit:]

        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Skip system messages
            if role == "system":
                continue

            timestamp = None
            if "created_at" in msg:
                if isinstance(msg["created_at"], str):
                    timestamp = datetime.fromisoformat(msg["created_at"])
                else:
                    timestamp = msg["created_at"]

            formatted.append(
                self.format_chat_message(
                    role=role,
                    content=content,
                    timestamp=timestamp,
                    include_timestamp=include_timestamps
                )
            )

        return "\n".join(formatted)

    def format_rag_response(
        self,
        answer: str,
        sources: List[Dict[str, Any]],
        format_type: str = "text",
        include_scores: bool = True
    ) -> str:
        """
        Format RAG response with sources

        Args:
            answer: AI-generated answer
            sources: List of source dictionaries
            format_type: Output format (text, markdown, json)
            include_scores: Whether to include similarity scores

        Returns:
            Formatted response
        """
        if format_type == "json":
            return self.format_json(
                content=answer,
                sources=sources,
                metadata={"source_count": len(sources)}
            )
        elif format_type == "markdown":
            return self.format_markdown(
                content=answer,
                include_sources=True,
                sources=sources,
                title="Answer"
            )
        else:
            return self.format_text(
                content=answer,
                include_sources=True,
                sources=sources
            )

    def _format_sources_text(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources as plain text"""
        if not sources:
            return ""

        lines = ["Sources:"]
        for i, source in enumerate(sources, 1):
            title = source.get("document_title", "Unknown")
            score = source.get("score", 0.0)
            lines.append(f"{i}. {title} (relevance: {score:.0%})")

        return "\n".join(lines)

    def _format_sources_markdown(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources as markdown list"""
        if not sources:
            return "No sources available."

        lines = []
        for i, source in enumerate(sources, 1):
            title = source.get("document_title", "Unknown")
            doc_id = source.get("document_id", "N/A")
            score = source.get("score", 0.0)
            chunk_index = source.get("chunk_index", "N/A")

            lines.append(
                f"{i}. **{title}** (Document ID: {doc_id}, "
                f"Chunk: {chunk_index}, Relevance: {score:.0%})"
            )

            # Add content preview if available
            preview = source.get("content_preview")
            if preview:
                lines.append(f"   > {preview}...")

        return "\n".join(lines)

    def _format_metadata_markdown(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as markdown"""
        lines = []

        # Token usage
        if "usage" in metadata:
            usage = metadata["usage"]
            lines.append(f"- **Total Tokens**: {usage.get('total_tokens', 0)}")
            lines.append(f"- **Prompt Tokens**: {usage.get('prompt_tokens', 0)}")
            lines.append(f"- **Completion Tokens**: {usage.get('completion_tokens', 0)}")

        # Model info
        if "model" in metadata:
            lines.append(f"- **Model**: {metadata['model']}")

        # RAG info
        if "has_context" in metadata:
            lines.append(f"- **RAG Enabled**: {metadata['has_context']}")

        if "search_results_count" in metadata:
            lines.append(f"- **Search Results**: {metadata['search_results_count']}")

        return "\n".join(lines) if lines else "No metadata available."

    def format_error(
        self,
        error_message: str,
        format_type: str = "text",
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format error message

        Args:
            error_message: Error message
            format_type: Output format (text, markdown, json)
            details: Additional error details

        Returns:
            Formatted error message
        """
        if format_type == "json":
            error_obj = {
                "status": "error",
                "error": error_message,
                "timestamp": datetime.now().isoformat()
            }
            if details:
                error_obj["details"] = details
            return json.dumps(error_obj, indent=2, ensure_ascii=False)

        elif format_type == "markdown":
            output = f"## Error\n\n{error_message}"
            if details:
                output += "\n\n### Details\n\n"
                output += "\n".join(f"- **{k}**: {v}" for k, v in details.items())
            return output

        else:
            output = f"Error: {error_message}"
            if details:
                output += "\nDetails: " + str(details)
            return output

    def format_summary(
        self,
        summary: str,
        statistics: Optional[Dict[str, Any]] = None,
        format_type: str = "text"
    ) -> str:
        """
        Format conversation summary

        Args:
            summary: Summary text
            statistics: Statistics dictionary
            format_type: Output format (text, markdown, json)

        Returns:
            Formatted summary
        """
        if format_type == "json":
            return self.format_json(
                content=summary,
                metadata=statistics
            )

        elif format_type == "markdown":
            output = [f"# Conversation Summary\n\n{summary}"]

            if statistics:
                output.append("\n## Statistics\n")
                for key, value in statistics.items():
                    formatted_key = key.replace("_", " ").title()
                    output.append(f"- **{formatted_key}**: {value}")

            return "\n".join(output)

        else:
            output = f"Summary: {summary}"
            if statistics:
                output += "\n\nStatistics:"
                for key, value in statistics.items():
                    formatted_key = key.replace("_", " ").title()
                    output += f"\n- {formatted_key}: {value}"
            return output


# Global formatter instance
response_formatter = ResponseFormatter()


def get_response_formatter() -> ResponseFormatter:
    """Get the global response formatter instance"""
    return response_formatter
