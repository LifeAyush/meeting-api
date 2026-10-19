import os


def whisper_model_name() -> str:
    return os.getenv("WHISPER_MODEL", "tiny")


def summary_mode() -> str:
    """mock | openai"""
    return os.getenv("SUMMARY_MODE", "mock").strip().lower()


def openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")
