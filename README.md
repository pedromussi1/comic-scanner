<h1 align="center">📚 Comic Book Scanner</h1>

<p align="center">
  <a href="https://youtu.be/Wwa3Uohue_4"><img src="https://i.imgur.com/RVu12mW.gif" alt="Comic Scanner Demo" width="800"></a>
</p>

<p align="center">A full-stack Flask app to identify comics and build a personal collection — by <b>barcode</b> when there is one, and by <b>cover image</b> when there isn't.</p>

<h3>🚀 Live app: <a href="https://huggingface.co/spaces/Zao0531/comic-scanner">huggingface.co/spaces/Zao0531/comic-scanner</a></h3>

## What it does

Upload a photo of a comic and the app tries two ways to identify it:

1. **Barcode** — if the image has an ISBN barcode, it's decoded with `pyzbar` and looked up
   via the **Google Books API** (title, author, publisher, date, cover).
2. **Cover recognition** — if there's no barcode, the cover is embedded with a **CLIP** vision
   model and matched against a **FAISS** index of reference covers (from Open Library). This
   is the same `comicid` engine used by
   [comic-recognizer](https://github.com/pedromussi1/comic-recognizer).

Identified comics can be added to a personal collection (per-user accounts, stored in a
database) and browsed later.

## Honest note on this rewrite

The previous README described a "trained deep-learning model (TensorFlow/Keras)" for cover
recognition — but the code never had one: recognition was **barcode-only**, and the
`requirements.txt` carried unused TensorFlow/pandas/scikit-learn (as a malformed UTF-16
file). This version **delivers the cover recognition it always claimed** (CLIP + FAISS, no
training required), trims the dependencies to what's actually used, and hardens the session
secret. No fabricated model, no dead weight.

## Stack

- **Flask** + **Flask-Login** (auth) + **Flask-SQLAlchemy** (SQLite locally, PostgreSQL in prod)
- **pyzbar** (barcode) + **Google Books API**
- **CLIP** (`sentence-transformers`) + **FAISS** (cover recognition)
- **Docker** + **Fly.io** deployment

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate            # (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt   # includes torch/CLIP — sizeable first install
python app.py                     # http://127.0.0.1:8000/
```

Notes:
- Barcode scanning needs the native **zbar** library. It's installed in the Docker image
  (`libzbar0`); on a bare dev box without it, the app still runs and cover recognition works
  (barcode is skipped gracefully).
- Set `SECRET_KEY` (and `DATABASE_URL` for PostgreSQL) in a `.env` file; without `SECRET_KEY`
  an ephemeral one is generated with a warning.

## Layout

```
app.py            routes: scan (barcode → cover fallback), auth, collection
database.py       SQLAlchemy models + queries
comicid/          shared CLIP + FAISS cover-recognition engine
data/index/       committed FAISS reference index
templates/        pages
tests/            pytest suite
Dockerfile, fly.toml   deployment
```

## Tests

```bash
python -m pytest -q
```
