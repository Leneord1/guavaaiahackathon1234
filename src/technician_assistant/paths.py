"""Application data paths."""

from pathlib import Path

from platformdirs import user_data_path

APP_NAME = "TechnicianVoiceAssistant"
DATA_DIR = Path(user_data_path(APP_NAME, appauthor="GuavaHackathon"))
DATABASE_PATH = DATA_DIR / "assistant.db"
MANUALS_DIR = DATA_DIR / "manuals"


def ensure_data_dirs() -> None:
    """Create local application directories."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MANUALS_DIR.mkdir(parents=True, exist_ok=True)
