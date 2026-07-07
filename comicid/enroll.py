"""Enroll your own cover photos into a personal reference index.

The Open Library demo index is great for famous graphic novels, but to recognize *your*
specific editions, index your own photos: take one clear photo of each comic's cover and
point this at the folder. CLIP matches future photos of the same edition very well.

Titles come from an optional labels CSV (``filename,title[,author]``); otherwise the file
name (without extension) is used as the title.

Run:
    python -m comicid.enroll path/to/cover_photos
    python -m comicid.enroll path/to/photos --labels labels.csv --output data/index
"""

from __future__ import annotations

import argparse
import csv
import os

from PIL import Image

from .embedder import Embedder
from .index import CoverIndex

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
_DEFAULT_OUTPUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "index")


def _load_labels(path: str) -> dict[str, dict]:
    """Map filename -> {title, author} from a CSV with a filename,title[,author] header."""
    labels = {}
    with open(path, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            fname = os.path.basename(row["filename"])
            labels[fname] = {"title": row.get("title", ""), "author": row.get("author", "")}
    return labels


def build_index_from_folder(
    folder: str, labels_csv: str | None = None, base_index: CoverIndex | None = None
) -> CoverIndex:
    """Embed every image in ``folder`` into a CoverIndex (title from labels or filename).

    Pass ``base_index`` to append the enrolled covers to an existing index (e.g. the demo
    Open Library index) instead of starting fresh.
    """
    labels = _load_labels(labels_csv) if labels_csv else {}
    files = sorted(f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in _IMAGE_EXTS)
    if not files:
        raise ValueError(f"No images found in {folder}")

    embedder = Embedder()
    images, metadata = [], []
    for fname in files:
        try:
            images.append(Image.open(os.path.join(folder, fname)).convert("RGB"))
        except Exception as exc:
            print(f"  ! skipping {fname}: {exc}")
            continue
        info = labels.get(fname, {})
        title = info.get("title") or os.path.splitext(fname)[0]
        metadata.append({
            "title": title,
            "author": info.get("author", ""),
            "cover_image": "",          # the enrolled photo is the user's own; nothing to link
            "source_url": "",
        })

    index = base_index or CoverIndex(dim=embedder.dim)
    index.add(embedder.embed_images(images), metadata)
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a personal cover index from your photos.")
    parser.add_argument("folder", help="folder of cover photos (one per comic)")
    parser.add_argument("--labels", help="optional CSV: filename,title[,author]")
    parser.add_argument("--output", default=_DEFAULT_OUTPUT, help="index output dir")
    parser.add_argument("--append", action="store_true",
                        help="append to the existing index at --output instead of replacing it")
    args = parser.parse_args()

    base = CoverIndex.load(args.output) if args.append and os.path.exists(
        os.path.join(args.output, "cover.index")) else None
    before = len(base) if base else 0
    index = build_index_from_folder(args.folder, args.labels, base_index=base)
    index.save(args.output)
    print(f"\nEnrolled {len(index) - before} covers "
          f"({'appended -> ' if before else ''}{len(index)} total) -> {args.output}")


if __name__ == "__main__":
    main()
