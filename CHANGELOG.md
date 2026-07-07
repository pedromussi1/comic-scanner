# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-07-07

### Added
- **Live hosted demo** on Hugging Face Spaces:
  https://huggingface.co/spaces/Zao0531/comic-scanner (with a persistent Neon Postgres for
  accounts + collections). Auto-syncs from `main` via a GitHub Action.

### Fixed
- Serverless-Postgres connection drops (Neon): enable SQLAlchemy `pool_pre_ping` +
  `pool_recycle` so dropped idle connections are revived instead of erroring.

## [2.1.0] - 2026-07-07

### Added
- Modern, responsive, dark-mode-aware UI matching the other apps: a shared base template
  with nav, a drag-and-drop scan page with image preview + loading state, a card-grid
  collection with search/sort/edit/delete, and clean login/signup pages.

### Removed
- Unused `templates/edit_comic.html` (editing happens via the collection modal).

## [2.0.2] - 2026-07-07

### Changed
- Cover fallback now uses the ~200-cover index that includes an enrolled 54-title personal
  collection; synced `enroll --append` from comic-recognizer.

## [2.0.1] - 2026-07-07

### Changed
- Expanded the shared cover-recognition index to ~45 titles / 121 covers (from ~20), and
  added `comicid/enroll.py` to build a personal index from your own cover photos.

## [2.0.0] - 2026-07-07

### Added
- **Cover recognition** (CLIP + FAISS) as a fallback when an uploaded image has no barcode —
  finally delivering the capability the README always claimed. Reuses the shared `comicid`
  engine (and reference index) from comic-recognizer. Cover matches are shown with their
  confidence and can be added to the collection (deduped by their Open Library id).

### Changed
- Rewrote the README to describe what the app actually does (barcode + cover recognition),
  replacing the false "trained deep-learning model (TensorFlow/Keras)" claim.
- Replaced the malformed UTF-16 `requirements.txt` and removed unused heavy dependencies
  (tensorflow, scikit-learn, opencv, pandas, aiohttp, google-api-python-client).

### Fixed / Security
- Removed the predictable hardcoded `"supersecretkey"` fallback; the app now uses
  `SECRET_KEY` from the environment or a generated ephemeral key (with a warning).
- Guarded the `pyzbar` import so the app runs where the native zbar library is absent
  (cover recognition still works; barcode scanning is skipped gracefully).
- Added a `pytest` suite.

[2.2.0]: https://github.com/pedromussi1/comic-scanner/releases/tag/v2.2.0
[2.1.0]: https://github.com/pedromussi1/comic-scanner/releases/tag/v2.1.0
[2.0.2]: https://github.com/pedromussi1/comic-scanner/releases/tag/v2.0.2
[2.0.1]: https://github.com/pedromussi1/comic-scanner/releases/tag/v2.0.1
[2.0.0]: https://github.com/pedromussi1/comic-scanner/releases/tag/v2.0.0
