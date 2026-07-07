"""High-level cover recognizer: load the index once, identify query images."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .embedder import Embedder
from .index import CoverIndex

_DEFAULT_INDEX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "index")


@dataclass
class Match:
    title: str
    author: str
    score: float           # cosine similarity in [-1, 1]
    cover_image: str       # local path or URL of the reference cover
    source_url: str        # Open Library work/edition link

    @property
    def confident(self) -> bool:
        # CLIP cosine for a genuine cover match typically lands well above this.
        return self.score >= 0.75


class CoverRecognizer:
    """Identify a comic from a cover photo against a prebuilt reference index."""

    def __init__(self, index_dir: str = _DEFAULT_INDEX_DIR, embedder: Embedder | None = None):
        self.index_dir = index_dir
        self.embedder = embedder or Embedder()
        self._index: CoverIndex | None = None

    @property
    def index(self) -> CoverIndex:
        if self._index is None:
            self._index = CoverIndex.load(self.index_dir)
        return self._index

    def identify(self, image_path: str, k: int = 5) -> list[Match]:
        emb = self.embedder.embed_image_path(image_path)
        results = self.index.query(emb, k=k)
        return [
            Match(
                title=meta.get("title", "Unknown"),
                author=meta.get("author", "Unknown"),
                score=score,
                cover_image=meta.get("cover_image", ""),
                source_url=meta.get("source_url", ""),
            )
            for meta, score in results
        ]
