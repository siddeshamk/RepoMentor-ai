"""
FAISS vector store: builds and persists per-repository semantic search indices.
"""
import json
import os
import pickle
from pathlib import Path
from typing import Any, Optional

import numpy as np

from app.config import settings
from app.ai.embeddings import embedding_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Per-repository FAISS index with associated metadata."""

    def __init__(self, repo_id: str):
        self.repo_id = repo_id
        self.index_dir = settings.indices_dir / repo_id
        self.index_path = self.index_dir / "index.faiss"
        self.meta_path = self.index_dir / "metadata.pkl"
        self._index = None
        self._metadata: list[dict] = []

    def build(self, chunks: list[dict]):
        """
        Build a FAISS index from text chunks.
        Each chunk must have 'text' and optionally 'file', 'line', 'type'.
        """
        try:
            import faiss
        except ImportError:
            raise RuntimeError("faiss-cpu not installed. Run: pip install faiss-cpu")

        if not chunks:
            logger.warning("No chunks provided to build vector store")
            return

        texts = [c["text"] for c in chunks if c.get("text", "").strip()]
        if not texts:
            return

        logger.info(f"Building FAISS index for repo {self.repo_id}: {len(texts)} chunks")
        embeddings = embedding_service.encode(texts)

        # Create flat L2 index (IP = inner product for normalized vectors = cosine similarity)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)  # Inner product (cosine) since vectors are normalized
        index.add(embeddings.astype(np.float32))

        self._index = index
        self._metadata = chunks

        # Persist to disk
        self.index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(self.index_path))
        with open(self.meta_path, "wb") as f:
            pickle.dump(chunks, f)

        logger.info(f"✅ FAISS index saved: {len(texts)} vectors at {self.index_dir}")

    def load(self) -> bool:
        """Load index from disk. Returns True if successful."""
        try:
            import faiss
            if not self.index_path.exists():
                return False
            self._index = faiss.read_index(str(self.index_path))
            with open(self.meta_path, "rb") as f:
                self._metadata = pickle.load(f)
            return True
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            return False

    def search(self, query: str, k: int = 8) -> list[dict]:
        """
        Search for the top-k most relevant chunks for a query.
        Returns list of chunk dicts with 'score' added.
        """
        if self._index is None:
            if not self.load():
                return []

        try:
            q_vec = embedding_service.encode_single(query).astype(np.float32)
            q_vec = q_vec.reshape(1, -1)

            k = min(k, self._index.ntotal)
            if k == 0:
                return []

            scores, indices = self._index.search(q_vec, k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self._metadata):
                    continue
                chunk = dict(self._metadata[idx])
                chunk["score"] = float(score)
                results.append(chunk)

            return results
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []

    def exists(self) -> bool:
        """Check if a built index exists on disk."""
        return self.index_path.exists() and self.meta_path.exists()


def prepare_repo_chunks(
    tree_data: dict,
    tech_data: dict,
    file_analyses: dict,
    docs_data: Optional[dict] = None,
) -> list[dict]:
    """
    Build a list of text chunks from repository analysis data.
    These chunks will be embedded and stored in FAISS.
    """
    chunks = []

    # 1. Technology overview
    langs = ", ".join(t["name"] for t in tech_data.get("languages", []))
    frameworks = ", ".join(f["name"] for f in tech_data.get("frameworks", []))
    chunks.append({
        "text": f"Technology stack: Languages: {langs}. Frameworks and tools: {frameworks}.",
        "type": "tech_overview",
        "file": "__tech__",
    })

    # 2. File-level chunks
    for rel_path, analysis in file_analyses.items():
        if not analysis:
            continue

        parts = []
        purpose = analysis.get("purpose", "")
        if purpose:
            parts.append(f"File: {rel_path}. Purpose: {purpose}.")

        classes = analysis.get("classes", [])
        if classes:
            class_names = ", ".join(c.get("name", "") for c in classes[:10])
            parts.append(f"Classes: {class_names}.")

        functions = analysis.get("functions", [])
        if functions:
            func_names = ", ".join(
                f.get("name", "") if isinstance(f, dict) else str(f)
                for f in functions[:15]
            )
            parts.append(f"Functions: {func_names}.")

        imports = analysis.get("imports", [])
        if imports:
            parts.append(f"Imports: {', '.join(imports[:10])}.")

        text = " ".join(parts)
        if len(text) > 50:
            chunks.append({
                "text": text,
                "type": "file_analysis",
                "file": rel_path,
            })

    # 3. Documentation chunks (if available)
    if docs_data:
        for doc_key, doc_content in docs_data.items():
            if isinstance(doc_content, str) and len(doc_content) > 100:
                # Split long docs into smaller chunks
                paragraphs = doc_content.split("\n\n")
                for para in paragraphs:
                    if len(para.strip()) > 80:
                        chunks.append({
                            "text": para.strip()[:1000],
                            "type": f"doc_{doc_key}",
                            "file": f"__docs__{doc_key}",
                        })

    logger.info(f"Prepared {len(chunks)} chunks for embedding")
    return chunks
