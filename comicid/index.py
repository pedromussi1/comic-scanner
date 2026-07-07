"""A FAISS cover index with aligned metadata, persistable to disk.

Exact inner-product search (``IndexFlatIP``) over L2-normalized CLIP embeddings = cosine
similarity. At reference-set scale (dozens–thousands of covers) exact search is instant; the
same code scales to an approximate index if the library ever grows large.
"""

from __future__ import annotations

import json
import os

import numpy as np


class CoverIndex:
    """Holds cover embeddings + per-cover metadata (title, author, image path, ...)."""

    def __init__(self, dim: int):
        import faiss

        self.dim = dim
        self._index = faiss.IndexFlatIP(dim)
        self.metadata: list[dict] = []

    def add(self, embeddings: np.ndarray, metadata: list[dict]) -> None:
        if len(embeddings) != len(metadata):
            raise ValueError("embeddings and metadata must be the same length")
        self._index.add(np.asarray(embeddings, dtype="float32"))
        self.metadata.extend(metadata)

    def query(self, embedding: np.ndarray, k: int = 5) -> list[tuple[dict, float]]:
        """Return up to k (metadata, cosine_similarity) pairs, best first."""
        if self._index.ntotal == 0:
            return []
        vec = np.asarray(embedding, dtype="float32").reshape(1, -1)
        k = min(k, self._index.ntotal)
        scores, ids = self._index.search(vec, k)
        return [(self.metadata[i], float(s)) for i, s in zip(ids[0], scores[0]) if i != -1]

    def __len__(self) -> int:
        return self._index.ntotal

    # -- persistence -------------------------------------------------------------
    def save(self, directory: str) -> None:
        import faiss

        os.makedirs(directory, exist_ok=True)
        faiss.write_index(self._index, os.path.join(directory, "cover.index"))
        with open(os.path.join(directory, "metadata.json"), "w", encoding="utf-8") as fh:
            json.dump(self.metadata, fh, indent=2)

    @classmethod
    def load(cls, directory: str) -> "CoverIndex":
        import faiss

        index = faiss.read_index(os.path.join(directory, "cover.index"))
        obj = cls.__new__(cls)
        obj._index = index
        obj.dim = index.d
        with open(os.path.join(directory, "metadata.json"), "r", encoding="utf-8") as fh:
            obj.metadata = json.load(fh)
        return obj
