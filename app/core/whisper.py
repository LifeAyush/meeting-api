from __future__ import annotations

import whisper

from app.core.config import whisper_model_name

_model = None


def get_whisper_model():
    """Lazy-load Whisper so tests can mock before first use."""
    global _model
    if _model is None:
        _model = whisper.load_model(whisper_model_name())
    return _model


def reset_whisper_model() -> None:
    """Clear the cached model (tests only)."""
    global _model
    _model = None


def transcribe_file(path: str) -> str:
    result = get_whisper_model().transcribe(path)
    return (result.get("text") or "").strip()
