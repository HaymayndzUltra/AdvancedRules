#!/usr/bin/env python3
"""
AdvancedRules Chroma Vector Database Adapter
Local-first vector storage with metadata filtering
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class ChromaAdapter:
    """ChromaDB adapter for vector storage and retrieval"""

    def __init__(self, persist_dir: str = ".cache/chroma", collection_name: str = "advanced_rules_memory"):
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize ChromaDB client and collection"""
        try:
            import chromadb
            from chromadb.config import Settings

            # Create persist directory
            self.persist_dir.mkdir(parents=True, exist_ok=True)

            # Initialize client
            self.client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False)
            )

            # Get or create collection
            try:
                self.collection = self.client.get_collection(self.collection_name)
                logger.info(f"Using existing collection: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "AdvancedRules hybrid memory store"}
                )
                logger.info(f"Created new collection: {self.collection_name}")

            self._initialized = True
            logger.info("ChromaDB adapter initialized successfully")
            return True

        except ImportError as e:
            logger.warning(f"ChromaDB not available: {e}")
            logger.warning("Install with: pip install chromadb")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            return False

    def store_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Store documents with embeddings and metadata"""
        if not self._initialized:
            logger.error("ChromaDB not initialized")
            return False

        try:
            ids = []
            texts = []
            metadatas = []
            embeddings_list = []

            for doc in documents:
                # Generate unique ID
                content_hash = hashlib.sha256(doc["content"].encode()).hexdigest()[:16]
                doc_id = f"{doc.get('namespace', 'default')}_{content_hash}"

                # Prepare data
                ids.append(doc_id)
                texts.append(doc["content"])
                metadatas.append({
                    "namespace": doc.get("namespace", "default"),
                    "source": doc.get("source", "unknown"),
                    "chunk_id": doc.get("chunk_id", 0),
                    "timestamp": doc.get("timestamp", ""),
                    "file_path": doc.get("file_path", ""),
                    "persona": doc.get("persona", "general"),
                })

                # Use pre-computed embeddings if available
                if "embedding" in doc:
                    embeddings_list.append(doc["embedding"])

            # Add to collection
            if embeddings_list:
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                    embeddings=embeddings_list
                )
            else:
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )

            logger.info(f"Stored {len(documents)} documents")
            return True

        except Exception as e:
            logger.error(f"Failed to store documents: {e}")
            return False

    def query_documents(self, query_text: str, embedding: List[float],
                       n_results: int = 8, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Query documents using vector similarity"""
        if not self._initialized:
            logger.error("ChromaDB not initialized")
            return []

        try:
            # Prepare query - ChromaDB has limitations with complex where clauses
            # For now, we'll do a simple query and filter results in Python
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=min(n_results * 3, 100),  # Get more results to filter
                include=["documents", "metadatas", "distances"]
            )

            # Format and filter results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0.0

                    # Apply metadata filtering in Python
                    if filter_metadata:
                        match = True
                        for key, expected_values in filter_metadata.items():
                            if key == "persona" and "$in" in expected_values:
                                actual_value = metadata.get("persona", "").lower()
                                if actual_value not in [v.lower() for v in expected_values["$in"]]:
                                    match = False
                                    break
                            elif key == "namespace" and "$in" in expected_values:
                                actual_value = metadata.get("namespace", "")
                                if actual_value not in expected_values["$in"]:
                                    match = False
                                    break
                            # Add more filter types as needed
                        if not match:
                            continue

                    formatted_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "score": 1.0 - distance,  # Convert distance to similarity
                        "source": metadata.get("source", "unknown"),
                        "namespace": metadata.get("namespace", "default"),
                        "file_path": metadata.get("file_path", ""),
                        "persona": metadata.get("persona", "general"),
                    })

            # Limit to requested number of results
            formatted_results = formatted_results[:n_results]

            logger.info(f"Query returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            return []

    def delete_by_metadata(self, metadata_filter: Dict[str, Any]) -> bool:
        """Delete documents matching metadata filter"""
        if not self._initialized:
            logger.error("ChromaDB not initialized")
            return False

        try:
            self.collection.delete(where=metadata_filter)
            logger.info(f"Deleted documents matching: {metadata_filter}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        if not self._initialized:
            return {"error": "ChromaDB not initialized"}

        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "persist_dir": str(self.persist_dir),
            }
        except Exception as e:
            return {"error": str(e)}

    def list_namespaces(self) -> List[str]:
        """List all available namespaces"""
        if not self._initialized:
            return []

        try:
            # Get all documents with metadata
            results = self.collection.get(include=["metadatas"])
            namespaces = set()

            if results["metadatas"]:
                for metadata in results["metadatas"]:
                    if "namespace" in metadata:
                        namespaces.add(metadata["namespace"])

            return sorted(list(namespaces))

        except Exception as e:
            logger.error(f"Failed to list namespaces: {e}")
            return []

    def purge_namespace(self, namespace: str) -> bool:
        """Purge all documents in a namespace"""
        return self.delete_by_metadata({"namespace": namespace})

    def purge_all(self) -> bool:
        """Purge all documents"""
        if not self._initialized:
            return False

        try:
            # Delete entire collection and recreate
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "AdvancedRules hybrid memory store"}
            )
            logger.info("Purged all documents")
            return True
        except Exception as e:
            logger.error(f"Failed to purge all documents: {e}")
            return False


class FallbackVectorStore:
    """Fallback vector store when ChromaDB is not available"""

    def __init__(self, persist_dir: str = ".cache/fallback"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.documents = []
        self._load_documents()

    def _load_documents(self):
        """Load documents from disk"""
        docs_file = self.persist_dir / "documents.json"
        if docs_file.exists():
            try:
                with open(docs_file, 'r') as f:
                    self.documents = json.load(f)
            except:
                self.documents = []

    def _save_documents(self):
        """Save documents to disk"""
        docs_file = self.persist_dir / "documents.json"
        try:
            with open(docs_file, 'w') as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save documents: {e}")

    def store_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Store documents (simple list append)"""
        for doc in documents:
            doc_copy = doc.copy()
            doc_copy["id"] = f"{doc.get('namespace', 'default')}_{hash(doc['content']) % 1000000}"
            self.documents.append(doc_copy)

        self._save_documents()
        logger.info(f"Stored {len(documents)} documents in fallback store")
        return True

    def query_documents(self, query_text: str, embedding: List[float],
                       n_results: int = 8, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Simple text matching query (no embeddings)"""
        results = []
        query_lower = query_text.lower()

        for doc in self.documents:
            # Simple filtering
            if filter_metadata:
                match = True
                for key, value in filter_metadata.items():
                    if doc.get("metadata", {}).get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            # Simple text matching
            content_lower = doc["content"].lower()
            score = 0.0

            # Word overlap scoring
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                score = overlap / len(query_words)

            if score > 0:
                results.append({
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {}),
                    "score": score,
                    "source": doc.get("source", "unknown"),
                    "namespace": doc.get("namespace", "default"),
                    "file_path": doc.get("file_path", ""),
                    "persona": doc.get("persona", "general"),
                })

        # Sort by score and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:n_results]

    def delete_by_metadata(self, metadata_filter: Dict[str, Any]) -> bool:
        """Delete documents matching metadata"""
        original_count = len(self.documents)
        self.documents = [
            doc for doc in self.documents
            if not all(doc.get("metadata", {}).get(k) == v for k, v in metadata_filter.items())
        ]
        if len(self.documents) != original_count:
            self._save_documents()
            return True
        return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get basic statistics"""
        return {
            "total_documents": len(self.documents),
            "store_type": "fallback",
            "persist_dir": str(self.persist_dir),
        }

    def list_namespaces(self) -> List[str]:
        """List namespaces"""
        namespaces = set()
        for doc in self.documents:
            namespaces.add(doc.get("namespace", "default"))
        return sorted(list(namespaces))

    def purge_namespace(self, namespace: str) -> bool:
        """Purge namespace"""
        original_count = len(self.documents)
        self.documents = [
            doc for doc in self.documents
            if doc.get("namespace") != namespace
        ]
        if len(self.documents) != original_count:
            self._save_documents()
            return True
        return False

    def purge_all(self) -> bool:
        """Purge all documents"""
        self.documents = []
        self._save_documents()
        return True


def create_vector_store(backend: str = "chroma", persist_dir: str = ".cache/chroma") -> Any:
    """Factory function to create vector store"""
    if backend.lower() == "chroma":
        store = ChromaAdapter(persist_dir)
        if store.initialize():
            return store
        else:
            logger.warning("ChromaDB failed, falling back to simple store")
            return FallbackVectorStore(persist_dir.replace("chroma", "fallback"))
    else:
        logger.info(f"Using fallback store for backend: {backend}")
        return FallbackVectorStore(persist_dir.replace("chroma", "fallback"))
