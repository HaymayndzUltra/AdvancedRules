#!/usr/bin/env python3
"""
AdvancedRules Embeddings Module
GPU-accelerated embeddings with graceful degradation
"""

import os
import logging
from typing import List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class EmbeddingProvider:
    """Base class for embedding providers"""

    def __init__(self, model_name: str, device: str = "auto"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the embedding model"""
        raise NotImplementedError

    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Encode texts to embeddings"""
        raise NotImplementedError

    def __call__(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Convenience method for encoding"""
        return self.encode(texts)


class BGEEmbeddingProvider(EmbeddingProvider):
    """BGE-M3 embeddings with GPU acceleration"""

    def __init__(self, model_name: str = "BAAI/bge-m3", device: str = "auto"):
        super().__init__(model_name, device)
        self.tokenizer = None

    def initialize(self) -> bool:
        """Initialize BGE-M3 model"""
        try:
            # Try to import torch and transformers
            import torch
            from transformers import AutoTokenizer, AutoModel

            # Determine device
            if self.device == "auto":
                self.device = _pick_device()

            logger.info(f"Initializing BGE embeddings on device: {self.device}")

            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)

            # Move to device if CUDA available
            if self.device == "cuda" and hasattr(torch, 'cuda') and torch.cuda.is_available():
                self.model = self.model.cuda()

            self._initialized = True
            logger.info("BGE embeddings initialized successfully")
            return True

        except ImportError as e:
            logger.warning(f"BGE dependencies not available: {e}")
            logger.warning("Install with: pip install torch transformers")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize BGE model: {e}")
            return False

    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Encode texts using BGE-M3"""
        if not self._initialized:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        if isinstance(texts, str):
            texts = [texts]

        try:
            import torch

            # Tokenize
            inputs = self.tokenizer(
                texts,
                max_length=8192,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )

            # Move to device
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}

            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state[:, 0]  # CLS token

            # Normalize
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

            # Convert to list
            return embeddings.cpu().tolist()

        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            # Return zero embeddings as fallback
            return [[0.0] * 1024 for _ in texts]  # BGE-M3 has 1024 dimensions


class SentenceTransformerProvider(EmbeddingProvider):
    """Sentence Transformers fallback"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "auto"):
        super().__init__(model_name, device)

    def initialize(self) -> bool:
        """Initialize Sentence Transformers model"""
        try:
            from sentence_transformers import SentenceTransformer

            if self.device == "auto":
                self.device = _pick_device()

            logger.info(f"Initializing Sentence Transformers on device: {self.device}")

            # Load model
            device_arg = 0 if self.device == "cuda" else -1  # SentenceTransformers uses device indices
            self.model = SentenceTransformer(self.model_name, device=device_arg)
            self._initialized = True
            logger.info("Sentence Transformers initialized successfully")
            return True

        except ImportError as e:
            logger.warning(f"Sentence Transformers not available: {e}")
            logger.warning("Install with: pip install sentence-transformers")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Sentence Transformers: {e}")
            return False

    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Encode texts using Sentence Transformers"""
        if not self._initialized:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        if isinstance(texts, str):
            texts = [texts]

        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            # Return zero embeddings as fallback
            return [[0.0] * 384 for _ in texts]  # Default dimension


class FallbackEmbeddingProvider(EmbeddingProvider):
    """Simple fallback when no ML libraries available"""

    def __init__(self, model_name: str = "fallback", device: str = "cpu"):
        super().__init__(model_name, device)
        self.dimension = 384  # Standard dimension

    def initialize(self) -> bool:
        """Always succeeds for fallback"""
        self._initialized = True
        logger.info("Using fallback embedding provider (no ML acceleration)")
        return True

    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Generate simple hash-based embeddings"""
        if isinstance(texts, str):
            texts = [texts]

        embeddings = []
        for text in texts:
            # Simple hash-based embedding (deterministic)
            import hashlib
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()

            # Convert to float list
            embedding = []
            for i in range(0, len(hash_bytes), 4):
                chunk = hash_bytes[i:i+4]
                if len(chunk) == 4:
                    value = int.from_bytes(chunk, byteorder='big') / (2**32 - 1)
                    embedding.append(value * 2 - 1)  # Scale to [-1, 1]
                else:
                    embedding.append(0.0)

            # Pad or truncate to dimension
            if len(embedding) < self.dimension:
                embedding.extend([0.0] * (self.dimension - len(embedding)))
            else:
                embedding = embedding[:self.dimension]

            embeddings.append(embedding)

        return embeddings


def _pick_device():
    """Safely pick the best available device"""
    try:
        import torch
        if hasattr(torch, 'cuda') and torch.cuda.is_available():
            return "cuda"
    except (ImportError, AttributeError):
        pass
    return "cpu"


def create_embedding_provider(model_name: str = "bge-m3",
                            device: str = "auto") -> EmbeddingProvider:
    """Factory function to create appropriate embedding provider"""

    if device == "auto":
        device = _pick_device()

    providers = [
        ("bge-m3", BGEEmbeddingProvider, "BAAI/bge-m3"),
        ("bge", BGEEmbeddingProvider, "BAAI/bge-large-en-v1.5"),
        ("sentence-transformers", SentenceTransformerProvider, "all-MiniLM-L6-v2"),
        ("fallback", FallbackEmbeddingProvider, "fallback"),
    ]

    # Try each provider in order of preference
    for provider_key, provider_class, default_model in providers:
        if provider_key in model_name.lower() or model_name.lower() in ["auto", "default"]:
            try:
                provider = provider_class(default_model if "auto" in model_name.lower() else model_name, device)
                if provider.initialize():
                    logger.info(f"Using embedding provider: {provider_key} on {device}")
                    return provider
            except Exception as e:
                logger.warning(f"Failed to initialize {provider_key}: {e}")
                continue

    # Final fallback
    logger.warning("All embedding providers failed, using fallback")
    provider = FallbackEmbeddingProvider()
    provider.initialize()
    return provider


def get_embedding_dimension(model_name: str) -> int:
    """Get expected embedding dimension for model"""
    dimensions = {
        "bge-m3": 1024,
        "bge-large": 1024,
        "all-MiniLM-L6-v2": 384,
        "all-MiniLM-L12-v2": 384,
        "paraphrase-MiniLM-L6-v2": 384,
        "fallback": 384,
    }

    for key, dim in dimensions.items():
        if key in model_name.lower():
            return dim

    return 384  # Default
