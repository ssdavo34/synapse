"""
Qdrant Vector Store Setup for SynapseSimple v2.0

Local file-based vector storage using Qdrant
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Optional, List, Dict, Any
import os

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    CollectionInfo
)

from config import settings
from utils.logger import setup_logger


class VectorStore:
    """Qdrant vector store manager with local file storage"""

    # Collection configuration
    COLLECTION_NAME = "chunk_embeddings"
    VECTOR_SIZE = 1536  # text-embedding-3-small dimension
    DISTANCE_METRIC = Distance.COSINE

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.qdrant_path = settings.qdrant_path

        # Ensure storage directory exists
        os.makedirs(self.qdrant_path, exist_ok=True)

        # Initialize Qdrant client with local file storage
        self.client = QdrantClient(path=str(self.qdrant_path))

        self.logger.info(f"Qdrant client initialized: {self.qdrant_path}")

        # Create collection if not exists
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Ensure the chunk_embeddings collection exists"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if self.COLLECTION_NAME not in collection_names:
                self.logger.info(f"Creating collection: {self.COLLECTION_NAME}")
                self._create_collection()
            else:
                self.logger.info(f"Collection already exists: {self.COLLECTION_NAME}")

        except Exception as e:
            self.logger.error(f"Error ensuring collection: {e}")
            raise

    def _create_collection(self) -> None:
        """Create the chunk_embeddings collection"""
        try:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=self.DISTANCE_METRIC
                )
            )

            self.logger.info(
                f"✅ Collection created: {self.COLLECTION_NAME} "
                f"(size={self.VECTOR_SIZE}, distance={self.DISTANCE_METRIC})"
            )

        except Exception as e:
            self.logger.error(f"Failed to create collection: {e}")
            raise

    def recreate_collection(self) -> None:
        """Delete and recreate the collection (use with caution!)"""
        try:
            self.logger.warning(f"⚠️ Recreating collection: {self.COLLECTION_NAME}")

            # Delete if exists
            try:
                self.client.delete_collection(collection_name=self.COLLECTION_NAME)
                self.logger.info("Old collection deleted")
            except Exception:
                pass  # Collection might not exist

            # Create new collection
            self._create_collection()

        except Exception as e:
            self.logger.error(f"Failed to recreate collection: {e}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information and statistics"""
        try:
            info: CollectionInfo = self.client.get_collection(
                collection_name=self.COLLECTION_NAME
            )

            return {
                "name": self.COLLECTION_NAME,
                "vector_size": self.VECTOR_SIZE,
                "distance": str(self.DISTANCE_METRIC),
                "points_count": info.points_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "status": info.status
            }

        except Exception as e:
            self.logger.error(f"Failed to get collection info: {e}")
            return {}

    def upsert_point(
        self,
        point_id: str,
        vector: List[float],
        payload: Dict[str, Any]
    ) -> bool:
        """Insert or update a single point"""
        try:
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )

            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[point]
            )

            self.logger.debug(f"Point upserted: {point_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to upsert point {point_id}: {e}")
            return False

    def upsert_points_batch(
        self,
        point_ids: List[str],
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]]
    ) -> int:
        """Insert or update multiple points in batch"""
        try:
            if not (len(point_ids) == len(vectors) == len(payloads)):
                raise ValueError("Length mismatch: point_ids, vectors, and payloads must have same length")

            points = [
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
                for point_id, vector, payload in zip(point_ids, vectors, payloads)
            ]

            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points
            )

            self.logger.info(f"✅ Batch upserted: {len(points)} points")
            return len(points)

        except Exception as e:
            self.logger.error(f"Failed to batch upsert: {e}")
            return 0

    def search_similar(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        try:
            # Build filter if provided
            query_filter = None
            if filter_conditions:
                query_filter = self._build_filter(filter_conditions)

            # Perform search
            search_result = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter
            )

            # Format results
            results = []
            for scored_point in search_result:
                results.append({
                    "id": scored_point.id,
                    "score": scored_point.score,
                    "payload": scored_point.payload
                })

            self.logger.debug(f"Search found {len(results)} results")
            return results

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []

    def _build_filter(self, conditions: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from conditions"""
        must_conditions = []

        for field, value in conditions.items():
            must_conditions.append(
                FieldCondition(
                    key=field,
                    match=MatchValue(value=value)
                )
            )

        return Filter(must=must_conditions)

    def delete_by_id(self, point_id: str) -> bool:
        """Delete a point by ID"""
        try:
            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=[point_id]
            )

            self.logger.debug(f"Point deleted: {point_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete point {point_id}: {e}")
            return False

    def delete_by_filter(self, filter_conditions: Dict[str, Any]) -> int:
        """Delete points matching filter conditions"""
        try:
            query_filter = self._build_filter(filter_conditions)

            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=query_filter
            )

            self.logger.info(f"Points deleted with filter: {filter_conditions}")
            return 1  # Qdrant doesn't return count for filter deletes

        except Exception as e:
            self.logger.error(f"Failed to delete by filter: {e}")
            return 0

    def delete_by_document(self, document_id: int) -> int:
        """Delete all vectors for a document"""
        return self.delete_by_filter({"document_id": document_id})

    def get_point(self, point_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a point by ID"""
        try:
            points = self.client.retrieve(
                collection_name=self.COLLECTION_NAME,
                ids=[point_id]
            )

            if points:
                point = points[0]
                return {
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload
                }

            return None

        except Exception as e:
            self.logger.error(f"Failed to get point {point_id}: {e}")
            return None

    def count_points(self, filter_conditions: Optional[Dict[str, Any]] = None) -> int:
        """Count points in collection"""
        try:
            if filter_conditions:
                query_filter = self._build_filter(filter_conditions)
                result = self.client.count(
                    collection_name=self.COLLECTION_NAME,
                    count_filter=query_filter
                )
            else:
                result = self.client.count(collection_name=self.COLLECTION_NAME)

            return result.count

        except Exception as e:
            self.logger.error(f"Failed to count points: {e}")
            return 0

    def health_check(self) -> bool:
        """Check if vector store is healthy"""
        try:
            info = self.get_collection_info()
            return bool(info)
        except Exception:
            return False


# Global vector store instance
vector_store = VectorStore()


def get_vector_store() -> VectorStore:
    """Get the global vector store instance"""
    return vector_store


def init_vector_store() -> None:
    """Initialize vector store (ensure collection exists)"""
    vector_store._ensure_collection()
