#!/usr/bin/env python3
"""Generate a short mono PCM WAV fixture (no third-party deps)."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fixtures" / "demo.wav"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 16_000
    duration_s = 1.0
    frequency = 440.0
    amplitude = 0.2
    n_frames = int(sample_rate * duration_s)

    with wave.open(str(OUT), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_frames):
            value = int(amplitude * 32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            frames.extend(struct.pack("<h", value))
        wf.writeframes(frames)

    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
