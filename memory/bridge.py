#!/usr/bin/env python3
"""
AdvancedRules Memory Bridge
Persona-aware retrieval interface for RAG integration
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class MemoryBridge:
    """Bridge between personas and memory system"""

    def __init__(self):
        self.vector_store = None
        self.embedding_provider = None
        self.config = {}
        self._initialized = False

        # Persona namespace mappings
        self.persona_namespaces = {
            "CODER_AI": ["coder", "tests"],
            "AUDITOR_AI": ["docs", "tests", "coder"],
            "PRINCIPAL_ENGINEER_AI": ["docs", "coder", "tests"],
            "PROJECT_MANAGER_AI": ["docs", "tests"],
            "DEVOPS_AI": ["docs", "tests", "coder"],
            "SECURITY_AI": ["docs", "tests", "coder"],
            "QA_AI": ["tests", "docs"],
            "GENERAL_AI": ["docs", "coder"],
        }

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize memory bridge with configuration"""
        try:
            self.config = config
            self._load_components()
            self._initialized = True
            logger.info("Memory bridge initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize memory bridge: {e}")
            self._initialized = False
            return False

    def _load_components(self):
        """Load vector store and embedding provider"""
        from .vector.chroma_adapter import create_vector_store
        from .vector.embeddings import create_embedding_provider

        # Initialize vector store
        backend = self.config.get("backend", "chroma")
        persist_dir = self.config.get("persist_dir", ".cache/chroma")
        self.vector_store = create_vector_store(backend, persist_dir)

        # Initialize embedding provider
        embedding_model = self.config.get("embedding_model", "bge-m3")
        self.embedding_provider = create_embedding_provider(embedding_model)

        logger.info(f"Loaded vector store: {backend}")
        logger.info(f"Loaded embedding model: {embedding_model}")

    def persona_context(self, persona: str, query: str, k: int = 8,
                       namespaces: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Retrieve context for a persona based on query"""
        if not self._is_enabled():
            logger.debug("RAG memory disabled, returning empty context")
            return []

        if not self._initialized:
            logger.warning("Memory bridge not initialized")
            return []

        try:
            # Determine namespaces for persona
            if namespaces is None:
                namespaces = self.persona_namespaces.get(persona.upper(), ["docs"])

            # Create metadata filter
            filter_metadata = {"persona": {"$in": [persona.lower()]}}
            if namespaces:
                filter_metadata["namespace"] = {"$in": namespaces}

            # Generate embedding for query
            query_embedding = self.embedding_provider.encode(query)[0]

            # Query vector store
            results = self.vector_store.query_documents(
                query_text=query,
                embedding=query_embedding,
                n_results=k,
                filter_metadata=filter_metadata
            )

            # Log retrieval metrics
            logger.info(f"Retrieved {len(results)} documents for {persona} (k={k})")
            if results:
                avg_score = sum(r["score"] for r in results) / len(results)
                logger.debug(f"Average retrieval score: {avg_score:.3f}")

            return results

        except Exception as e:
            logger.error(f"Failed to retrieve context for {persona}: {e}")
            return []

    def store_context(self, persona: str, content: str, source: str = "unknown",
                     namespace: str = "general", metadata: Optional[Dict] = None) -> bool:
        """Store context for a persona"""
        if not self._is_enabled():
            logger.debug("RAG memory disabled, skipping storage")
            return True  # Don't fail, just skip

        if not self._initialized:
            logger.warning("Memory bridge not initialized")
            return False

        try:
            # Prepare document
            doc = {
                "content": content,
                "namespace": namespace,
                "source": source,
                "persona": persona.lower(),
                "timestamp": self._get_timestamp(),
            }

            # Add custom metadata
            if metadata:
                doc.update(metadata)

            # Generate embedding
            embedding = self.embedding_provider.encode(content)[0]
            doc["embedding"] = embedding

            # Store in vector store
            success = self.vector_store.store_documents([doc])

            if success:
                logger.info(f"Stored context for {persona} in namespace {namespace}")
            else:
                logger.error(f"Failed to store context for {persona}")

            return success

        except Exception as e:
            logger.error(f"Failed to store context for {persona}: {e}")
            return False

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        if not self._initialized:
            return {"status": "not_initialized"}

        try:
            stats = self.vector_store.get_collection_stats()
            namespaces = self.vector_store.list_namespaces()

            return {
                "status": "active",
                "backend": self.config.get("backend", "unknown"),
                "embedding_model": self.config.get("embedding_model", "unknown"),
                "namespaces": namespaces,
                "vector_store": stats,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _is_enabled(self) -> bool:
        """Check if RAG memory is enabled"""
        # Check feature flag
        features_enabled = self.config.get("features", {}).get("rag_memory", False)

        # Check environment variable
        env_enabled = os.getenv("AR_ENABLE_RAG", "0") == "1"

        return features_enabled or env_enabled

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def purge_persona_memory(self, persona: str) -> bool:
        """Purge all memory for a specific persona"""
        if not self._initialized:
            return False

        try:
            # Get all namespaces for this persona
            namespaces = self.persona_namespaces.get(persona.upper(), [])

            success = True
            for namespace in namespaces:
                if not self.vector_store.purge_namespace(namespace):
                    success = False

            if success:
                logger.info(f"Purged memory for {persona}")
            else:
                logger.error(f"Failed to purge some namespaces for {persona}")

            return success

        except Exception as e:
            logger.error(f"Failed to purge memory for {persona}: {e}")
            return False

    def purge_all_memory(self) -> bool:
        """Purge all memory (dangerous operation)"""
        if not self._initialized:
            return False

        try:
            success = self.vector_store.purge_all()
            if success:
                logger.warning("Purged all memory")
            else:
                logger.error("Failed to purge all memory")

            return success

        except Exception as e:
            logger.error(f"Failed to purge all memory: {e}")
            return False


# Global memory bridge instance
_memory_bridge = None

def get_memory_bridge() -> MemoryBridge:
    """Get or create global memory bridge instance"""
    global _memory_bridge
    if _memory_bridge is None:
        _memory_bridge = MemoryBridge()
    return _memory_bridge

def persona_context(persona: str, query: str, k: int = 8,
                   namespaces: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Main entry point for persona-aware context retrieval"""
    bridge = get_memory_bridge()

    # Initialize if not already done (lazy loading)
    if not bridge._initialized:
        # Try to load config from standard location
        config_path = Path("config/advanced_rules.yaml")
        if config_path.exists():
            try:
                import yaml
                with open(config_path, 'r') as f:
                    full_config = yaml.safe_load(f)
                    rag_config = full_config.get("rag", {})
                    bridge.initialize(rag_config)
            except Exception as e:
                logger.warning(f"Failed to load config for memory bridge: {e}")

    return bridge.persona_context(persona, query, k, namespaces)

def store_persona_context(persona: str, content: str, source: str = "unknown",
                         namespace: str = "general", metadata: Optional[Dict] = None) -> bool:
    """Store context for a persona"""
    bridge = get_memory_bridge()
    return bridge.store_context(persona, content, source, namespace, metadata)

# Backwards compatibility aliases
retrieve_context = persona_context
store_memory = store_persona_context
