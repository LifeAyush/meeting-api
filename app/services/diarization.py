from __future__ import annotations

import io
import tempfile
import wave

import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

_encoder: VoiceEncoder | None = None


def get_encoder() -> VoiceEncoder:
    global _encoder
    if _encoder is None:
        _encoder = VoiceEncoder()
    return _encoder


def reset_encoder() -> None:
    global _encoder
    _encoder = None


def _wav_bytes_to_array(audio_bytes: bytes) -> tuple[np.ndarray, int]:
    """Decode PCM WAV bytes to float32 mono samples and sample rate."""
    with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
        sample_rate = wf.getframerate()
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())

    if sample_width == 2:
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif sample_width == 4:
        audio = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        audio = np.frombuffer(frames, dtype=np.uint8).astype(np.float32)
        audio = (audio - 128.0) / 128.0

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    return audio, sample_rate


def get_speaker_embeddings(audio_bytes: bytes) -> np.ndarray:
    """Extract a speaker embedding from raw WAV bytes."""
    try:
        audio, sample_rate = _wav_bytes_to_array(audio_bytes)
        wav = preprocess_wav(audio, sample_rate)
    except Exception:
        # Fallback: write bytes and let Resemblyzer load the path (handles more formats).
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            wav = preprocess_wav(tmp.name)
    return get_encoder().embed_utterance(wav)


def match_speaker(
    embedding: np.ndarray,
    buffers: dict[str, list[np.ndarray]],
    threshold: float = 0.75,
) -> str:
    """Match embedding to an existing speaker id or allocate a new one."""
    import uuid

    for speaker_id, emb_list in buffers.items():
        sim = float(np.inner(embedding, np.mean(emb_list, axis=0)))
        if sim > threshold:
            buffers[speaker_id].append(embedding)
            return speaker_id

    speaker_id = str(uuid.uuid4())[:8]
    buffers[speaker_id] = [embedding]
    return speaker_id
