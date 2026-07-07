"""comicid: identify a comic/graphic novel from a photo of its cover.

Uses CLIP image embeddings + a FAISS nearest-neighbor index over a reference set of covers.
No training: adding a comic means embedding one cover image and inserting it into the index.
"""

from .embedder import Embedder
from .index import CoverIndex
from .recognizer import CoverRecognizer, Match

__all__ = ["Embedder", "CoverIndex", "CoverRecognizer", "Match"]
