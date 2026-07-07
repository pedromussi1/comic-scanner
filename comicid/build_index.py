"""Build the reference cover index from free Open Library cover thumbnails.

For each comic in COMICS: search Open Library, download its cover, embed it with CLIP, and
save a FAISS index + metadata. Raw covers are downloaded to data/covers/ (gitignored, only
needed at build time); the committed index (embeddings) + metadata let the app run without
re-downloading. Reference covers are displayed at runtime via their Open Library URL.

Run:  python -m comicid.build_index      (add --comics to override the default list)
"""

from __future__ import annotations

import argparse
import os
import re
import time

import requests
from PIL import Image

from .embedder import Embedder
from .index import CoverIndex

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVERS_DIR = os.path.join(HERE, "data", "covers")
INDEX_DIR = os.path.join(HERE, "data", "index")
_SEARCH_URL = "https://openlibrary.org/search.json"
_COVER_URL = "https://covers.openlibrary.org/b/id/{cid}-{size}.jpg"

# Well-known graphic novels Open Library reliably has covers for. Author included to
# disambiguate the search. Add your own comics here (or via --comics) and rebuild.
COMICS = [
    ("Watchmen", "Alan Moore"),
    ("V for Vendetta", "Alan Moore"),
    ("Batman The Killing Joke", "Alan Moore"),
    ("Batman Year One", "Frank Miller"),
    ("The Dark Knight Returns", "Frank Miller"),
    ("Batman The Long Halloween", "Jeph Loeb"),
    ("Batman Hush", "Jeph Loeb"),
    ("The Sandman", "Neil Gaiman"),
    ("Maus", "Art Spiegelman"),
    ("Persepolis", "Marjane Satrapi"),
    ("Saga Volume 1", "Brian K. Vaughan"),
    ("Y The Last Man", "Brian K. Vaughan"),
    ("Sin City", "Frank Miller"),
    ("Fun Home", "Alison Bechdel"),
    ("Kingdom Come", "Mark Waid"),
    ("Superman Red Son", "Mark Millar"),
    ("Daredevil Born Again", "Frank Miller"),
    ("House of X", "Jonathan Hickman"),
    ("New X-Men", "Grant Morrison"),
    ("Blankets", "Craig Thompson"),
    ("Bone", "Jeff Smith"),
    ("Preacher", "Garth Ennis"),
    ("Hellboy Seed of Destruction", "Mike Mignola"),
    ("Scott Pilgrim", "Bryan Lee O'Malley"),
]


_STOPWORDS = {"the", "of", "a", "an", "and", "vol", "volume", "book", "deluxe", "edition"}


def _slug(title: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in title.lower()).strip("_")


def _keywords(title: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in _STOPWORDS}


def _find_covers(title: str, author: str, max_editions: int = 4) -> list[dict]:
    """Return up to ``max_editions`` distinct covers whose title matches ``title``.

    Indexing several editions per comic makes recognition robust: a query photo matches if it
    resembles *any* edition, not just one. Open Library's first hit is often a generic or
    wrong edition, so candidates are scored by keyword overlap with the intended title.
    """
    params = {"q": f"{title} {author}", "limit": 20,
              "fields": "title,author_name,key,cover_i"}
    resp = requests.get(_SEARCH_URL, params=params, timeout=20)
    resp.raise_for_status()

    want = _keywords(title)
    out, seen = [], set()
    for doc in resp.json().get("docs", []):
        cid = doc.get("cover_i")
        if not cid or cid in seen:
            continue
        if not (_keywords(doc.get("title", "")) & want):  # must share a distinctive word
            continue
        seen.add(cid)
        authors = doc.get("author_name") or [author]
        out.append({
            "title": title,  # clean intended title for display
            "author": authors[0],
            "cover_id": cid,
            "source_url": "https://openlibrary.org" + doc.get("key", ""),
        })
        if len(out) >= max_editions:
            break
    return out


def _download_cover(cover_id: int, path: str) -> bool:
    resp = requests.get(_COVER_URL.format(cid=cover_id, size="L"), timeout=20)
    if resp.status_code != 200 or len(resp.content) < 1000:  # OL returns a tiny blank on miss
        return False
    with open(path, "wb") as fh:
        fh.write(resp.content)
    return True


def build(comics: list[tuple[str, str]]) -> CoverIndex:
    os.makedirs(COVERS_DIR, exist_ok=True)
    embedder = Embedder()
    images, metadata = [], []
    seen_covers: set[int] = set()

    for title, author in comics:
        try:
            covers = _find_covers(title, author)
        except requests.RequestException as exc:
            print(f"  ! search failed for {title}: {exc}")
            continue
        if not covers:
            print(f"  - no cover found for {title}")
            continue

        added = 0
        for info in covers:
            cid = info["cover_id"]
            if cid in seen_covers:
                continue
            seen_covers.add(cid)

            path = os.path.join(COVERS_DIR, f"{_slug(title)}_{cid}.jpg")
            if not os.path.exists(path) and not _download_cover(cid, path):
                continue
            try:
                images.append(Image.open(path).convert("RGB"))
            except Exception:  # corrupt download
                continue

            metadata.append({
                "title": info["title"],
                "author": info["author"],
                "cover_image": _COVER_URL.format(cid=cid, size="M"),
                "source_url": info["source_url"],
            })
            added += 1
            time.sleep(0.15)  # be polite to Open Library
        print(f"  + {title}: {added} edition(s)")

    print(f"\nEmbedding {len(images)} covers with CLIP...")
    index = CoverIndex(dim=embedder.dim)
    if images:
        index.add(embedder.embed_images(images), metadata)
    index.save(INDEX_DIR)
    print(f"Saved index with {len(index)} covers to {INDEX_DIR}")
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the comic cover reference index.")
    parser.add_argument("--comics", nargs="*", help="override titles (space-separated, quoted)")
    args = parser.parse_args()
    comics = [(t, "") for t in args.comics] if args.comics else COMICS
    build(comics)


if __name__ == "__main__":
    main()
