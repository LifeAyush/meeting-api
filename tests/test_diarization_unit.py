from __future__ import annotations

import math
import struct
import wave
from io import BytesIO

import numpy as np

from app.services.diarization import _wav_bytes_to_array, match_speaker


def test_wav_bytes_to_array():
    buffer = BytesIO()
    sample_rate = 16_000
    with wave.open(buffer, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(800):
            value = int(0.1 * 32767 * math.sin(2 * math.pi * 220 * i / sample_rate))
            frames.extend(struct.pack("<h", value))
        wf.writeframes(frames)

    audio, rate = _wav_bytes_to_array(buffer.getvalue())
    assert rate == sample_rate
    assert audio.dtype == np.float32
    assert len(audio) == 800


def test_match_speaker_scopes_buffers():
    buffers: dict[str, list] = {}
    emb_a = np.ones(8, dtype=np.float32)
    emb_b = -np.ones(8, dtype=np.float32)

    speaker_a = match_speaker(emb_a, buffers, threshold=0.9)
    again = match_speaker(emb_a * 0.99, buffers, threshold=0.5)
    speaker_b = match_speaker(emb_b, buffers, threshold=0.9)

    assert again == speaker_a
    assert speaker_b != speaker_a
    assert set(buffers) == {speaker_a, speaker_b}
