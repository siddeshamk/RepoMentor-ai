"""
Embeddings service using sentence-transformers.
Encodes text into dense vectors for semantic search.
"""
from typing import Optional

import numpy as np

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Wrapper around sentence-transformers for generating text embeddings."""

    def __init__(self):
        self._model = None
        self._model_name = settings.embedding_model

    def _load_model(self):
        """Lazy-load the embedding model on first use."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self._model_name}")
                self._model = SentenceTransformer(self._model_name)
                logger.info("✅ Embedding model loaded")
            except ImportError:
                raise RuntimeError(
                    "sentence-transformers not installed. Run: pip install sentence-transformers"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to load embedding model: {e}") from e

    def encode(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        """
        Encode a list of strings into embedding vectors.
        Returns numpy array of shape (n_texts, embedding_dim).
        """
        self._load_model()
        if not texts:
            return np.array([])

        # Filter out empty strings
        texts = [t[:8192] for t in texts if t.strip()]  # Cap at 8192 chars

        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,
            convert_to_numpy=True,
            normalize_embeddings=True,  # L2-normalize for cosine similarity
        )
        return embeddings

    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single string into an embedding vector."""
        return self.encode([text])[0]

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        self._load_model()
        return self._model.get_sentence_embedding_dimension()


# Singleton
embedding_service = EmbeddingService()
