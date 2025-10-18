"""
Search Service for SynapseSimple v2.0

Semantic search with RAG (Retrieval-Augmented Generation) support
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Any, Optional
import json

from services.vector_store_service import vector_store_service
from services.database_service import db_service
from services.embedding_service import EmbeddingService
from utils.text_processor import TextProcessor
from utils.logger import setup_logger


class SearchService:
    """Semantic search service with RAG context building"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.vector_service = vector_store_service
        self.embedding_service = EmbeddingService()
        self.text_processor = TextProcessor()

        self.logger.info("Search Service initialized")

    async def semantic_search(
        self,
        query: str,
        user_id: Optional[int] = None,
        document_id: Optional[int] = None,
        limit: int = 5,
        score_threshold: float = 0.7,
        include_context: bool = False,
        max_context_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Perform semantic search across documents

        Args:
            query: Search query text
            user_id: Filter by user (optional)
            document_id: Filter by specific document (optional)
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)
            include_context: Build RAG context from results
            max_context_tokens: Maximum tokens for context

        Returns:
            Search results with chunks, scores, and optional context
        """
        try:
            self.logger.info(f"🔍 Semantic search: '{query[:50]}...'")

            # Validate query
            if not query or len(query.strip()) == 0:
                return {
                    "success": False,
                    "error": "Query cannot be empty",
                    "results": []
                }

            # Step 1: Search in vector store
            vector_results = await self.vector_service.search_similar(
                query=query,
                limit=limit,
                score_threshold=score_threshold,
                document_id=document_id
            )

            if not vector_results:
                self.logger.info("No results found in vector search")
                return {
                    "success": True,
                    "results": [],
                    "total": 0,
                    "query": query
                }

            # Step 2: Enrich results with database metadata
            chunk_ids = [result["chunk_id"] for result in vector_results]
            chunks = db_service.get_chunks_by_ids(chunk_ids)

            # Create chunk lookup
            chunk_lookup = {chunk.id: chunk for chunk in chunks}

            # Step 3: Get document metadata
            document_ids = list(set(result["document_id"] for result in vector_results))
            documents = {}
            for doc_id in document_ids:
                doc = db_service.get_document(doc_id)
                if doc:
                    documents[doc_id] = {
                        "id": doc.id,
                        "title": doc.title,
                        "file_type": doc.file_type,
                        "created_at": doc.created_at.isoformat() if doc.created_at else None
                    }

            # Step 4: Filter by user_id if specified
            if user_id:
                filtered_results = []
                for result in vector_results:
                    doc_id = result["document_id"]
                    if doc_id in documents:
                        doc = db_service.get_document(doc_id)
                        if doc and doc.user_id == user_id:
                            filtered_results.append(result)
                vector_results = filtered_results

            # Step 5: Build enriched results
            enriched_results = []
            for result in vector_results:
                chunk_id = result["chunk_id"]
                chunk = chunk_lookup.get(chunk_id)

                if not chunk:
                    continue

                enriched_results.append({
                    "chunk_id": chunk_id,
                    "document_id": result["document_id"],
                    "document_title": documents.get(result["document_id"], {}).get("title", "Unknown"),
                    "content": result["content"],
                    "chunk_index": result["chunk_index"],
                    "score": result["score"],
                    "token_count": result["token_count"]
                })

            # Step 6: Build RAG context if requested
            context = None
            if include_context and enriched_results:
                context = await self.vector_service.build_context(
                    search_results=vector_results,
                    max_tokens=max_context_tokens,
                    include_metadata=True
                )

            # Step 7: Calculate statistics
            total_documents = len(set(r["document_id"] for r in enriched_results))
            avg_score = sum(r["score"] for r in enriched_results) / len(enriched_results) if enriched_results else 0

            result = {
                "success": True,
                "query": query,
                "results": enriched_results,
                "total": len(enriched_results),
                "documents_searched": total_documents,
                "average_score": round(avg_score, 3),
                "score_threshold": score_threshold
            }

            if context:
                result["context"] = context

            self.logger.info(
                f"✅ Search complete: {len(enriched_results)} results "
                f"from {total_documents} documents"
            )

            return result

        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

    async def multi_query_search(
        self,
        queries: List[str],
        user_id: Optional[int] = None,
        limit: int = 3,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search multiple queries in parallel

        Args:
            queries: List of search queries
            user_id: Filter by user
            limit: Results per query
            score_threshold: Minimum score

        Returns:
            List of search results (one per query)
        """
        try:
            import asyncio

            tasks = [
                self.semantic_search(
                    query=query,
                    user_id=user_id,
                    limit=limit,
                    score_threshold=score_threshold
                )
                for query in queries
            ]

            results = await asyncio.gather(*tasks)
            return list(results)

        except Exception as e:
            self.logger.error(f"Multi-query search failed: {e}")
            return [{"success": False, "error": str(e)} for _ in queries]

    async def search_by_keywords(
        self,
        keywords: List[str],
        user_id: Optional[int] = None,
        limit: int = 5,
        score_threshold: float = 0.65
    ) -> Dict[str, Any]:
        """
        Search using multiple keywords (combines results)

        Args:
            keywords: List of keywords
            user_id: Filter by user
            limit: Total results to return
            score_threshold: Minimum score

        Returns:
            Combined and ranked search results
        """
        try:
            # Create search query from keywords
            query = " ".join(keywords)

            # Perform semantic search
            result = await self.semantic_search(
                query=query,
                user_id=user_id,
                limit=limit * 2,  # Get more results for better ranking
                score_threshold=score_threshold
            )

            if not result["success"]:
                return result

            # Re-rank results based on keyword matches
            ranked_results = []
            for item in result["results"]:
                content_lower = item["content"].lower()
                keyword_matches = sum(1 for kw in keywords if kw.lower() in content_lower)

                # Boost score based on keyword matches
                boosted_score = item["score"] + (keyword_matches * 0.05)
                item["boosted_score"] = min(boosted_score, 1.0)
                item["keyword_matches"] = keyword_matches

                ranked_results.append(item)

            # Sort by boosted score
            ranked_results.sort(key=lambda x: x["boosted_score"], reverse=True)

            # Limit results
            ranked_results = ranked_results[:limit]

            result["results"] = ranked_results
            result["total"] = len(ranked_results)
            result["keywords"] = keywords

            return result

        except Exception as e:
            self.logger.error(f"Keyword search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

    async def build_rag_context(
        self,
        query: str,
        user_id: Optional[int] = None,
        document_id: Optional[int] = None,
        max_tokens: int = 2000,
        min_chunks: int = 3,
        score_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Build RAG context for LLM prompts

        Args:
            query: User query
            user_id: Filter by user
            document_id: Filter by document
            max_tokens: Maximum context tokens
            min_chunks: Minimum chunks to include
            score_threshold: Minimum similarity score

        Returns:
            RAG context with formatted text and metadata
        """
        try:
            self.logger.info(f"📝 Building RAG context for: '{query[:50]}...'")

            # Search for relevant chunks
            search_result = await self.semantic_search(
                query=query,
                user_id=user_id,
                document_id=document_id,
                limit=min_chunks * 2,  # Get extra for filtering
                score_threshold=score_threshold,
                include_context=False
            )

            if not search_result["success"] or not search_result["results"]:
                return {
                    "success": False,
                    "error": "No relevant context found",
                    "context_text": "",
                    "chunks": []
                }

            # Build context using vector service
            context = await self.vector_service.build_context(
                search_results=search_result["results"],
                max_tokens=max_tokens,
                include_metadata=True
            )

            # Check if we have minimum chunks
            if context["chunk_count"] < min_chunks:
                self.logger.warning(
                    f"Only {context['chunk_count']} chunks found "
                    f"(minimum: {min_chunks})"
                )

            # Add query and metadata
            context["query"] = query
            context["success"] = True
            context["score_threshold"] = score_threshold

            self.logger.info(
                f"✅ RAG context built: {context['chunk_count']} chunks, "
                f"{context['total_tokens']} tokens"
            )

            return context

        except Exception as e:
            self.logger.error(f"Failed to build RAG context: {e}")
            return {
                "success": False,
                "error": str(e),
                "context_text": "",
                "chunks": []
            }

    async def find_similar_chunks(
        self,
        chunk_id: int,
        limit: int = 5,
        score_threshold: float = 0.7,
        exclude_same_document: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find chunks similar to a given chunk

        Args:
            chunk_id: Source chunk ID
            limit: Maximum results
            score_threshold: Minimum score
            exclude_same_document: Exclude chunks from same document

        Returns:
            List of similar chunks
        """
        try:
            # Get source chunk
            chunk = db_service.get_chunk(chunk_id)
            if not chunk:
                return []

            # Use chunk content as query
            results = await self.semantic_search(
                query=chunk.content,
                limit=limit + 1,  # +1 to account for self-match
                score_threshold=score_threshold
            )

            if not results["success"]:
                return []

            # Filter out source chunk and optionally same document
            filtered = []
            for result in results["results"]:
                if result["chunk_id"] == chunk_id:
                    continue

                if exclude_same_document and result["document_id"] == chunk.document_id:
                    continue

                filtered.append(result)

            return filtered[:limit]

        except Exception as e:
            self.logger.error(f"Find similar chunks failed: {e}")
            return []

    def get_search_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get search-related statistics

        Args:
            user_id: Filter by user (optional)

        Returns:
            Statistics dict
        """
        try:
            stats = {
                "vector_store": self.vector_service.get_collection_stats(),
                "total_vectors": 0,
                "total_documents": 0,
                "total_chunks": 0
            }

            # Get vector count
            vector_info = stats["vector_store"]
            stats["total_vectors"] = vector_info.get("total_vectors", 0)

            # Get document/chunk counts from database
            if user_id:
                user_stats = db_service.get_user_stats(user_id)
                stats["total_documents"] = user_stats.get("document_count", 0)
            else:
                # Count all documents
                docs = db_service.list_documents(limit=10000)
                stats["total_documents"] = len(docs)

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get search statistics: {e}")
            return {}


# Global search service instance
search_service = SearchService()


def get_search_service() -> SearchService:
    """Get the global search service instance"""
    return search_service
