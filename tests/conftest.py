from __future__ import annotations

import importlib

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def client(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("SUMMARY_MODE", "mock")
    monkeypatch.setenv("WHISPER_MODEL", "tiny")

    def fake_embeddings(audio_bytes: bytes) -> np.ndarray:
        return np.ones(256, dtype=np.float32)

    def fake_transcribe(path: str) -> str:
        return "hello from fixture"

    import app.db.session as session_mod

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session_mod.engine = engine
    session_mod.SessionLocal = testing_session
    session_mod.DATABASE_URL = db_url

    import app.models  # noqa: F401
    from app.models.base import Base

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr("app.services.diarization.get_speaker_embeddings", fake_embeddings)

    import app.main as main_mod

    main_mod = importlib.reload(main_mod)
    monkeypatch.setattr("app.api.v1.websocket.get_speaker_embeddings", fake_embeddings)
    monkeypatch.setattr("app.api.v1.websocket.transcribe_file", fake_transcribe)

    with TestClient(main_mod.app) as test_client:
        yield test_client
