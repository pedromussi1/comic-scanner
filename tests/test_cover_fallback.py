"""Cover-recognition fallback + zbar guard, with a stub recognizer (no CLIP)."""

from comicid.recognizer import Match


class _StubRecognizer:
    def __init__(self, match):
        self._match = match

    def identify(self, path, k=1):
        return [self._match] if self._match else []


def test_recognize_cover_maps_confident_match(monkeypatch):
    import app
    match = Match("Watchmen", "Alan Moore", 0.94, "http://cover",
                  "https://openlibrary.org/works/OL123W")
    monkeypatch.setattr(app, "get_recognizer", lambda: _StubRecognizer(match))

    result = app.recognize_cover("ignored.jpg")
    assert result["Title"] == "Watchmen"
    assert result["Source"] == "cover"
    assert result["Confidence"] == 0.94
    assert result["ISBN"] == "OL123W"          # OL id extracted as the dedup identifier
    assert result["Cover Image"] == "http://cover"


def test_recognize_cover_none_when_not_confident(monkeypatch):
    import app
    weak = Match("Whatever", "X", 0.40, "", "")   # below the 0.75 confidence threshold
    monkeypatch.setattr(app, "get_recognizer", lambda: _StubRecognizer(weak))
    assert app.recognize_cover("ignored.jpg") is None


def test_detect_isbn_returns_none_without_zbar(monkeypatch):
    import app
    monkeypatch.setattr(app, "_ZBAR_AVAILABLE", False)
    assert app.detect_isbn("ignored.jpg") is None
