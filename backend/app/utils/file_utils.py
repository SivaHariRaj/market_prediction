"""
File system utilities for AIgnition backend.
Handles upload path resolution and unique ID generation.
"""
import uuid
from pathlib import Path

UPLOADS_DIR = Path(__file__).parent.parent / "storage" / "uploads"


def ensure_uploads_dir() -> Path:
    """Create the uploads directory if it doesn't exist."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOADS_DIR


def generate_upload_id() -> str:
    """Return a short unique identifier for an upload session."""
    return uuid.uuid4().hex[:12]


def get_upload_path(upload_id: str, filename: str) -> Path:
    """Return the full path for a given upload_id + filename."""
    ensure_uploads_dir()
    return UPLOADS_DIR / f"{upload_id}_{filename}"


def find_upload_file(upload_id: str) -> Path | None:
    """
    Locate the file associated with an upload_id.
    Returns None if not found.
    """
    ensure_uploads_dir()
    matches = list(UPLOADS_DIR.glob(f"{upload_id}_*"))
    return matches[0] if matches else None


def sanitize_filename(name: str) -> str:
    """Strip dangerous characters from a filename."""
    return "".join(c for c in name if c.isalnum() or c in (".", "_", "-")).strip()
