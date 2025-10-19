"""
RAG (Retrieval-Augmented Generation) Pipeline

Integrates document search with conversation agent for context-aware responses
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Any, Optional
from datetime import datetime

from agents.conversation_agent import ConversationAgent
from services.search_service import SearchService
from services.database_service import DatabaseService
from utils.logger import setup_logger


class RAGPipeline:
    """
    RAG Pipeline for document-based question answering

    Workflow:
    1. User asks question
    2. Search relevant documents (vector search)
    3. Build context from search results
    4. Generate response with context
    5. Track sources and metadata
    """

    def __init__(
        self,
        conversation_agent: Optional[ConversationAgent] = None,
        search_service: Optional[SearchService] = None,
        db_service: Optional[DatabaseService] = None,
        default_search_limit: int = 5,
        default_score_threshold: float = 0.7,
        max_context_tokens: int = 2000
    ):
        """
        Initialize RAG pipeline

        Args:
            conversation_agent: Conversation agent instance
            search_service: Search service instance
            db_service: Database service instance
            default_search_limit: Default number of search results
            default_score_threshold: Default similarity score threshold
            max_context_tokens: Maximum tokens in context
        """
        self.agent = conversation_agent or ConversationAgent()
        self.search_service = search_service or SearchService()
        self.db_service = db_service or DatabaseService()

        self.default_search_limit = default_search_limit
        self.default_score_threshold = default_score_threshold
        self.max_context_tokens = max_context_tokens

        self.logger = setup_logger(__name__)

    def search_documents(
        self,
        query: str,
        user_id: Optional[int] = None,
        document_id: Optional[int] = None,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Search documents with semantic search

        Args:
            query: Search query
            user_id: Filter by user ID
            document_id: Filter by document ID
            limit: Maximum results
            score_threshold: Minimum similarity score

        Returns:
            Search results dictionary
        """
        try:
            limit = limit or self.default_search_limit
            score_threshold = score_threshold or self.default_score_threshold

            # Perform semantic search with context building
            results = self.search_service.semantic_search_sync(
                query=query,
                user_id=user_id,
                document_id=document_id,
                limit=limit,
                score_threshold=score_threshold,
                include_context=True,
                max_context_tokens=self.max_context_tokens
            )

            self.logger.info(
                f"Document search: query='{query[:50]}...', "
                f"results={results.get('count', 0)}, "
                f"has_context={results.get('has_context', False)}"
            )

            return results

        except Exception as e:
            self.logger.error(f"Document search error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "count": 0,
                "results": [],
                "has_context": False,
                "context": ""
            }

    def build_context(self, search_results: Dict[str, Any]) -> str:
        """
        Build context from search results

        Args:
            search_results: Search results dictionary

        Returns:
            Context string
        """
        # If search service already built context, use it
        if search_results.get("has_context") and search_results.get("context"):
            return search_results["context"]

        # Otherwise, build context manually
        results = search_results.get("results", [])
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            chunk = result.get("chunk", {})
            document = result.get("document", {})
            score = result.get("score", 0.0)

            # Format: [Source N] (Document: title, Score: 0.85)
            # Content...
            context_parts.append(
                f"[Source {i}] (Document: {document.get('title', 'Unknown')}, "
                f"Score: {score:.2f})\n{chunk.get('content', '')}"
            )

        return "\n\n".join(context_parts)

    def extract_sources(self, search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract source information from search results

        Args:
            search_results: Search results dictionary

        Returns:
            List of source dictionaries
        """
        sources = []
        results = search_results.get("results", [])

        for result in results:
            chunk = result.get("chunk", {})
            document = result.get("document", {})

            sources.append({
                "document_id": document.get("id"),
                "document_title": document.get("title"),
                "chunk_id": chunk.get("id"),
                "chunk_index": chunk.get("chunk_index"),
                "score": result.get("score"),
                "content_preview": chunk.get("content", "")[:200]
            })

        return sources

    def query(
        self,
        question: str,
        user_id: Optional[int] = None,
        document_id: Optional[int] = None,
        search_limit: Optional[int] = None,
        score_threshold: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query with RAG pipeline

        Args:
            question: User question
            user_id: Filter by user ID
            document_id: Filter by specific document
            search_limit: Maximum search results
            score_threshold: Minimum similarity score
            metadata: Additional metadata

        Returns:
            Response dictionary with answer and sources
        """
        try:
            self.logger.info(f"RAG query: '{question[:100]}...'")

            # Step 1: Search documents
            search_results = self.search_documents(
                query=question,
                user_id=user_id,
                document_id=document_id,
                limit=search_limit,
                score_threshold=score_threshold
            )

            if not search_results.get("success"):
                return {
                    "success": False,
                    "error": search_results.get("error", "Search failed"),
                    "answer": "I encountered an error searching the documents.",
                    "sources": [],
                    "has_context": False
                }

            # Step 2: Build context
            context = self.build_context(search_results)
            has_context = bool(context)

            # Step 3: Extract sources
            sources = self.extract_sources(search_results)

            # Step 4: Generate response with context
            if has_context:
                response = self.agent.chat_with_rag(
                    user_message=question,
                    context=context,
                    metadata=metadata
                )
            else:
                # No relevant documents found
                response = {
                    "success": True,
                    "content": "I don't have enough information in the provided documents to answer this question. Could you please rephrase or ask about a different topic?",
                    "finish_reason": "no_context",
                    "usage": {"total_tokens": 0},
                    "metadata": {}
                }

            # Step 5: Build final response
            result = {
                "success": True,
                "answer": response.get("content", ""),
                "sources": sources,
                "has_context": has_context,
                "search_results_count": search_results.get("count", 0),
                "finish_reason": response.get("finish_reason"),
                "usage": response.get("usage", {}),
                "metadata": {
                    "model": response.get("metadata", {}).get("model"),
                    "search_limit": search_limit or self.default_search_limit,
                    "score_threshold": score_threshold or self.default_score_threshold,
                    "timestamp": datetime.now().isoformat()
                }
            }

            self.logger.info(
                f"RAG response: has_context={has_context}, "
                f"sources={len(sources)}, "
                f"tokens={response.get('usage', {}).get('total_tokens', 0)}"
            )

            return result

        except Exception as e:
            self.logger.error(f"RAG query error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "answer": "I apologize, but I encountered an error processing your question.",
                "sources": [],
                "has_context": False
            }

    def query_simple(self, question: str, user_id: Optional[int] = None) -> str:
        """
        Simple query that returns just the answer text

        Args:
            question: User question
            user_id: Filter by user ID

        Returns:
            Answer text
        """
        result = self.query(question=question, user_id=user_id)
        return result.get("answer", "I couldn't generate an answer.")

    def query_with_sources(
        self,
        question: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query and format response with source citations

        Args:
            question: User question
            user_id: Filter by user ID

        Returns:
            Response with formatted sources
        """
        result = self.query(question=question, user_id=user_id)

        if not result.get("success"):
            return result

        # Format answer with sources
        answer = result["answer"]
        sources = result["sources"]

        if sources:
            answer += "\n\nSources:\n"
            for i, source in enumerate(sources, 1):
                answer += f"{i}. {source['document_title']} (relevance: {source['score']:.2%})\n"

        result["formatted_answer"] = answer
        return result

    def clear_conversation(self):
        """Clear conversation history"""
        self.agent.clear_history()
        self.logger.info("RAG conversation cleared")

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get conversation history

        Returns:
            List of message dictionaries
        """
        return self.agent.export_conversation()

    def get_conversation_summary(self) -> str:
        """
        Get conversation summary

        Returns:
            Summary string
        """
        return self.agent.get_conversation_summary()
