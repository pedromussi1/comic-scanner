"""Ingest comic covers from the Metron API (metron.cloud) into the reference index.

Scales the recognizer toward "any cover" by pulling real issue covers from an open comic
database. Metron uses HTTP Basic auth with your account username/password; provide them via
environment variables or a local ``.env`` file (never committed):

    METRON_USER=your_username
    METRON_PASSWORD=your_password

By default it targets popular series (recognizable comics). Use --all to crawl the catalog
alphabetically instead. The index is saved after each series, so an interruption keeps the
progress and re-running resumes (already-added covers are skipped by title).

Run:
    python -m comicid.ingest_metron                 # popular series, append + resumable
    python -m comicid.ingest_metron --cap 80        # up to 80 issues per series
    python -m comicid.ingest_metron --all --limit 3000   # alphabetical crawl instead
"""

from __future__ import annotations

import argparse
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import requests
from PIL import Image

from .embedder import Embedder
from .index import CoverIndex

_API = "https://metron.cloud/api"
_INDEX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "index")
_ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
_DELAY = 2.5             # be gentle: Metron rate-limits (~30 requests/minute)
_EMBED_BATCH = 128
_DOWNLOAD_WORKERS = 10

# Well-known series so the demo recognizes comics people actually own.
POPULAR_SERIES = [
    # Marvel
    "Amazing Spider-Man", "Uncanny X-Men", "X-Men", "New X-Men", "House of X", "Powers of X",
    "Avengers", "New Avengers", "Fantastic Four", "Daredevil", "Thor", "Iron Man",
    "Captain America", "Immortal Hulk", "Incredible Hulk", "Wolverine", "Venom", "Deadpool",
    "Black Panther", "Doctor Strange", "Moon Knight", "Punisher", "Silver Surfer",
    "Guardians of the Galaxy", "Ms. Marvel", "Captain Marvel", "Hawkeye", "Ant-Man",
    "Infinity Gauntlet", "Secret Wars", "Civil War", "Marvel Zombies",
    # DC
    "Batman", "Detective Comics", "Superman", "Action Comics", "Wonder Woman", "The Flash",
    "Green Lantern", "Justice League", "Aquaman", "Nightwing", "Batgirl", "Harley Quinn",
    "Teen Titans", "Swamp Thing", "The Sandman", "Watchmen", "Doomsday Clock", "Rorschach",
    "Joker", "Suicide Squad", "Green Arrow", "Shazam", "Constantine", "Batman: The Long Halloween",
    "Batman: Year One", "Batman: Hush", "The Dark Knight Returns", "Kingdom Come", "Superman: Red Son",
    # Image / other
    "Saga", "The Walking Dead", "Invincible", "Spawn", "Paper Girls", "Monstress", "Chew",
    "East of West", "Deadly Class", "Something is Killing the Children", "The Boys", "Hellboy",
    "Sin City", "Kick-Ass", "Y: The Last Man", "Fables", "Locke & Key", "Bone", "Sweet Tooth",
    "Descender", "Rat Queens", "Preacher", "Scott Pilgrim", "Maus", "Persepolis",
]


def _credentials() -> tuple[str, str]:
    user, pw = os.environ.get("METRON_USER"), os.environ.get("METRON_PASSWORD")
    if (not user or not pw) and os.path.exists(_ENV_FILE):
        for line in open(_ENV_FILE, encoding="utf-8"):
            line = line.strip()
            if line.startswith("METRON_USER="):
                user = user or line.split("=", 1)[1].strip()
            elif line.startswith("METRON_PASSWORD="):
                pw = pw or line.split("=", 1)[1].strip()
    if not user or not pw:
        raise SystemExit("Set METRON_USER and METRON_PASSWORD (env vars or a .env file).")
    return user, pw


def _get(auth, path_or_url, params=None, retries=6):
    url = path_or_url if path_or_url.startswith("http") else f"{_API}/{path_or_url}"
    delay = 10.0
    for attempt in range(retries):
        resp = requests.get(url, auth=auth, params=params or {}, timeout=30)
        if resp.status_code == 429 and attempt < retries - 1:
            wait = int(resp.headers.get("Retry-After", delay))
            print(f"  (rate-limited; waiting {wait}s)", flush=True)
            time.sleep(wait)
            delay *= 2
            continue
        if resp.status_code in (401, 403):
            raise SystemExit("Metron auth failed — check METRON_USER / METRON_PASSWORD.")
        resp.raise_for_status()
        return resp.json()
    raise SystemExit("Metron kept rate-limiting; try again later or lower the request rate.")


def _norm(s: str) -> str:
    s = re.sub(r"\(\d{4}\)|tpb|hc|omnibus|:", " ", (s or "").lower())
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^(the|a|an)\s+", "", s)   # ignore a leading article ("The Amazing...")


def _best_series(auth, name: str) -> dict | None:
    results = _get(auth, "series/", {"name": name}).get("results", [])
    want = _norm(name)
    scored = []
    for s in results:
        nm = _norm(s.get("series") or s.get("name") or "")
        scored.append((nm == want, nm.startswith(want), s.get("issue_count", 0), s))
    if not scored:
        return None
    scored.sort(key=lambda t: (t[0], t[1], t[2]), reverse=True)
    return scored[0][3]


def _issue_title(issue: dict) -> str:
    if issue.get("issue"):
        return issue["issue"]
    series = issue.get("series") or {}
    name = series.get("name") if isinstance(series, dict) else series
    return f"{name} #{issue.get('number', '')}".strip()


def _records_from_page(data: dict) -> list[dict]:
    return [{"title": _issue_title(i), "image": i["image"], "source_url": i.get("resource_url", "")}
            for i in data.get("results", []) if i.get("image")]


def _fetch_series_issues(auth, series_id: int, cap: int) -> list[dict]:
    got, url, params = [], "issue/", {"series_id": series_id, "page": 1}
    while url and len(got) < cap:
        data = _get(auth, url, params)
        got.extend(_records_from_page(data))
        url, params = data.get("next"), {}
        time.sleep(_DELAY)
    return got[:cap]


def _download(record: dict):
    try:
        resp = requests.get(record["image"], timeout=30)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        img.thumbnail((384, 384))
        return img, record
    except Exception:
        return None


def _add_records(index: CoverIndex, embedder: Embedder, records: list[dict], seen: set) -> int:
    imgs, metas, added = [], [], 0

    def flush():
        nonlocal added
        if imgs:
            index.add(embedder.embed_images(imgs), metas)
            added += len(imgs)
            imgs.clear(); metas.clear()

    with ThreadPoolExecutor(max_workers=_DOWNLOAD_WORKERS) as pool:
        for result in pool.map(_download, records):
            if result is None:
                continue
            img, rec = result
            if rec["title"] in seen:          # already indexed (resume / dedupe)
                continue
            seen.add(rec["title"])
            imgs.append(img)
            metas.append({"title": rec["title"], "author": "",
                          "cover_image": rec["image"], "source_url": rec["source_url"]})
            if len(imgs) >= _EMBED_BATCH:
                flush()
    flush()
    return added


def _load_or_new(embedder: Embedder, fresh: bool) -> CoverIndex:
    if not fresh:
        try:
            return CoverIndex.load(_INDEX_DIR)
        except Exception:
            pass
    return CoverIndex(dim=embedder.dim)


def ingest_series(auth, series_names, cap: int, fresh: bool) -> CoverIndex:
    embedder = Embedder()
    index = _load_or_new(embedder, fresh)
    seen = {m["title"] for m in index.metadata}
    for name in series_names:
        series = _best_series(auth, name)
        time.sleep(_DELAY)
        if not series:
            print(f"  - no series match for {name}", flush=True)
            continue
        records = _fetch_series_issues(auth, series["id"], cap)
        added = _add_records(index, embedder, records, seen)
        index.save(_INDEX_DIR)   # save after each series -> crash-resilient / resumable
        print(f"  + {series.get('series') or name}: +{added} (index now {len(index)})", flush=True)
    return index


def ingest_all(auth, limit: int, fresh: bool) -> CoverIndex:
    embedder = Embedder()
    index = _load_or_new(embedder, fresh)
    seen = {m["title"] for m in index.metadata}
    url, params, total = "issue/", {"page": 1}, 0
    while url and total < limit:
        data = _get(auth, url, params)
        total += _add_records(index, embedder, _records_from_page(data), seen)
        index.save(_INDEX_DIR)
        url, params = data.get("next"), {}
        print(f"  {total} covers scanned (index now {len(index)})", flush=True)
        time.sleep(_DELAY)
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest comic covers from Metron.")
    parser.add_argument("--all", action="store_true", help="crawl alphabetically instead of popular series")
    parser.add_argument("--limit", type=int, default=3000, help="max covers (alphabetical mode)")
    parser.add_argument("--cap", type=int, default=60, help="max issues per series (series mode)")
    parser.add_argument("--fresh", action="store_true", help="start a new index instead of appending")
    args = parser.parse_args()

    auth = _credentials()
    if args.all:
        print(f"Crawling up to {args.limit} issues alphabetically...", flush=True)
        index = ingest_all(auth, args.limit, args.fresh)
    else:
        print(f"Ingesting popular series (cap {args.cap} issues each)...", flush=True)
        index = ingest_series(auth, POPULAR_SERIES, args.cap, args.fresh)
    print(f"\nDone. Index has {len(index)} covers.", flush=True)


if __name__ == "__main__":
    main()
