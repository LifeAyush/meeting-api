import uuid
import base64
from pathlib import Path

TEMP_AUDIO_DIR = Path("temp_audio/")
TEMP_AUDIO_DIR.mkdir(exist_ok=True)

def save_base64_audio(chunk_base64: str, extension: str = "wav") -> Path:
    audio_data = base64.b64decode(chunk_base64)
    file_id = f"{uuid.uuid4()}.{extension}"
    file_path = TEMP_AUDIO_DIR / file_id
    with open(file_path, "wb") as f:
        f.write(audio_data)
    return file_path
