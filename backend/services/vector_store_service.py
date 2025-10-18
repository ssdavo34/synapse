"""
Vector Store Service for SynapseSimple v2.0

High-level service for vector operations with embedding integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Any, Optional
import asyncio

from services.vector_store import vector_store, VectorStore
from services.embedding_service import EmbeddingService
from utils.logger import setup_logger


class VectorStoreService:
    """High-level vector store service with embedding integration"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.vector_store: VectorStore = vector_store
        self.embedding_service = EmbeddingService()

        self.logger.info("Vector Store Service initialized")

    async def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None
    ) -> int:
        """
        Insert or update chunks with embeddings

        Args:
            chunks: List of chunk dicts with keys: id, document_id, content, chunk_index
            embeddings: Pre-computed embeddings (optional, will compute if not provided)

        Returns:
            Number of vectors successfully inserted
        """
        try:
            # Generate embeddings if not provided
            if embeddings is None:
                self.logger.info(f"Generating embeddings for {len(chunks)} chunks...")
                texts = [chunk["content"] for chunk in chunks]
                embeddings = await self.embedding_service.generate_embeddings(texts)

            if len(embeddings) != len(chunks):
                raise ValueError(f"Embedding count mismatch: {len(embeddings)} != {len(chunks)}")

            # Prepare data for Qdrant
            point_ids = []
            vectors = []
            payloads = []

            for chunk, embedding in zip(chunks, embeddings):
                point_id = f"chunk_{chunk['id']}"
                point_ids.append(point_id)
                vectors.append(embedding)

                payload = {
                    "chunk_id": chunk["id"],
                    "document_id": chunk["document_id"],
                    "content": chunk["content"],
                    "chunk_index": chunk.get("chunk_index", 0),
                    "token_count": chunk.get("token_count", 0)
                }
                payloads.append(payload)

            # Batch upsert to Qdrant
            count = self.vector_store.upsert_points_batch(
                point_ids=point_ids,
                vectors=vectors,
                payloads=payloads
            )

            self.logger.info(f"✅ Upserted {count} vectors")
            return count

        except Exception as e:
            self.logger.error(f"Failed to upsert chunks: {e}")
            raise

    async def search_similar(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.7,
        document_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using semantic search

        Args:
            query: Search query text
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)
            document_id: Filter by document ID (optional)
            user_id: Filter by user ID (optional, requires DB lookup)

        Returns:
            List of search results with chunk data and scores
        """
        try:
            # Generate query embedding
            self.logger.debug(f"Generating embedding for query: {query[:50]}...")
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Build filter conditions
            filter_conditions = {}
            if document_id:
                filter_conditions["document_id"] = document_id

            # Search in vector store
            results = self.vector_store.search_similar(
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filter_conditions if filter_conditions else None
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "chunk_id": result["payload"]["chunk_id"],
                    "document_id": result["payload"]["document_id"],
                    "content": result["payload"]["content"],
                    "chunk_index": result["payload"].get("chunk_index", 0),
                    "score": result["score"],
                    "token_count": result["payload"].get("token_count", 0)
                })

            self.logger.info(f"Found {len(formatted_results)} similar chunks (threshold={score_threshold})")
            return formatted_results

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []

    async def search_similar_batch(
        self,
        queries: List[str],
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[List[Dict[str, Any]]]:
        """
        Search for multiple queries in batch

        Args:
            queries: List of search queries
            limit: Maximum results per query
            score_threshold: Minimum similarity score

        Returns:
            List of result lists (one per query)
        """
        try:
            tasks = [
                self.search_similar(query, limit, score_threshold)
                for query in queries
            ]
            results = await asyncio.gather(*tasks)
            return list(results)

        except Exception as e:
            self.logger.error(f"Batch search failed: {e}")
            return [[] for _ in queries]

    def delete_by_chunk_id(self, chunk_id: int) -> bool:
        """Delete a vector by chunk ID"""
        try:
            point_id = f"chunk_{chunk_id}"
            success = self.vector_store.delete_by_id(point_id)

            if success:
                self.logger.debug(f"Deleted vector for chunk {chunk_id}")

            return success

        except Exception as e:
            self.logger.error(f"Failed to delete chunk {chunk_id}: {e}")
            return False

    def delete_by_document(self, document_id: int) -> int:
        """Delete all vectors for a document"""
        try:
            count = self.vector_store.delete_by_document(document_id)
            self.logger.info(f"Deleted vectors for document {document_id}")
            return count

        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id} vectors: {e}")
            return 0

    async def build_context(
        self,
        search_results: List[Dict[str, Any]],
        max_tokens: int = 2000,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Build context from search results for RAG

        Args:
            search_results: Results from search_similar()
            max_tokens: Maximum total tokens
            include_metadata: Include chunk metadata in response

        Returns:
            Context dict with formatted text and metadata
        """
        try:
            context_chunks = []
            total_tokens = 0
            documents_used = set()

            for result in search_results:
                chunk_tokens = result.get("token_count", 0)

                # Check if adding this chunk would exceed limit
                if total_tokens + chunk_tokens > max_tokens:
                    self.logger.debug(f"Token limit reached: {total_tokens}/{max_tokens}")
                    break

                context_chunks.append(result)
                total_tokens += chunk_tokens
                documents_used.add(result["document_id"])

            # Build formatted context text
            context_text_parts = []
            for i, chunk in enumerate(context_chunks, 1):
                context_text_parts.append(
                    f"[Chunk {i}] (Score: {chunk['score']:.3f})\n{chunk['content']}\n"
                )

            context_text = "\n---\n".join(context_text_parts)

            result = {
                "context_text": context_text,
                "total_tokens": total_tokens,
                "chunk_count": len(context_chunks),
                "document_count": len(documents_used)
            }

            if include_metadata:
                result["chunks"] = context_chunks
                result["document_ids"] = list(documents_used)

            self.logger.debug(
                f"Built context: {len(context_chunks)} chunks, "
                f"{total_tokens} tokens, {len(documents_used)} documents"
            )

            return result

        except Exception as e:
            self.logger.error(f"Failed to build context: {e}")
            return {
                "context_text": "",
                "total_tokens": 0,
                "chunk_count": 0,
                "document_count": 0
            }

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            info = self.vector_store.get_collection_info()
            return {
                "collection_name": info.get("name"),
                "total_vectors": info.get("points_count", 0),
                "vector_dimension": info.get("vector_size"),
                "distance_metric": info.get("distance"),
                "status": info.get("status")
            }

        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {}

    def health_check(self) -> bool:
        """Check if vector store service is healthy"""
        try:
            return self.vector_store.health_check()
        except Exception:
            return False

    async def reindex_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Reindex chunks in batches (useful for rebuilding index)

        Args:
            chunks: List of chunks to reindex
            batch_size: Number of chunks per batch

        Returns:
            Total number of vectors reindexed
        """
        try:
            total_indexed = 0

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                count = await self.upsert_chunks(batch)
                total_indexed += count

                self.logger.info(f"Reindexed batch {i//batch_size + 1}: {count} vectors")

            self.logger.info(f"✅ Reindexing complete: {total_indexed} total vectors")
            return total_indexed

        except Exception as e:
            self.logger.error(f"Reindexing failed: {e}")
            return 0


# Global service instance
vector_store_service = VectorStoreService()


def get_vector_store_service() -> VectorStoreService:
    """Get the global vector store service instance"""
    return vector_store_service
