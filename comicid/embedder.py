"""CLIP embedding of cover images (and text), via sentence-transformers.

``clip-ViT-B-32`` maps images and text into the same 512-d space, so covers can be matched
image-to-image (a photo vs. reference covers) and, if useful, text-to-image. Embeddings are
L2-normalized, so an inner-product FAISS index gives cosine similarity.
"""

from __future__ import annotations

from PIL import Image

_MODEL_NAME = "clip-ViT-B-32"


class Embedder:
    """Lazy CLIP encoder. Construct once; reuse for many images."""

    def __init__(self, model_name: str = _MODEL_NAME):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # heavy, lazy import

            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def dim(self) -> int:
        return self._get_model().get_sentence_embedding_dimension()

    def embed_images(self, images: list[Image.Image]):
        """Return an (N, dim) float32 array of L2-normalized image embeddings."""
        return self._get_model().encode(
            images, convert_to_numpy=True, normalize_embeddings=True
        )

    def embed_image_path(self, path: str):
        img = Image.open(path).convert("RGB")
        return self.embed_images([img])[0]

    def embed_text(self, texts: list[str]):
        return self._get_model().encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        )
