"""
AIgnition — Upload Service
Handles file persistence, CSV parsing and metadata extraction.
"""
import shutil
from pathlib import Path

from fastapi import UploadFile

from app.models.response_models import UploadResponse
from app.utils.csv_utils import detect_platform, load_csv, dataframe_summary
from app.utils.exceptions import InvalidCSV, UnsupportedFileType
from app.utils.file_utils import generate_upload_id, get_upload_path, sanitize_filename
from app.utils.logger import get_logger
from app.config import settings

logger = get_logger(__name__)

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


async def handle_upload(file: UploadFile, source: str | None = None) -> UploadResponse:
    """
    Persist the uploaded CSV and return file metadata.

    Steps:
      1. Validate file extension and size.
      2. Generate a unique upload_id.
      3. Save file to storage/uploads/.
      4. Parse CSV to extract row/column info.
      5. Auto-detect platform if source not provided.
    """
    # ── 1. Validate extension ─────────────────────────────────────────────
    filename = sanitize_filename(file.filename or "upload.csv")
    if not filename.lower().endswith(".csv"):
        raise UnsupportedFileType(filename)

    # ── 2. Generate ID ────────────────────────────────────────────────────
    upload_id = generate_upload_id()
    dest: Path = get_upload_path(upload_id, filename)

    # ── 3. Save file ──────────────────────────────────────────────────────
    try:
        total = 0
        with dest.open("wb") as out:
            while chunk := await file.read(65536):
                total += len(chunk)
                if total > MAX_BYTES:
                    dest.unlink(missing_ok=True)
                    raise InvalidCSV(
                        f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB."
                    )
                out.write(chunk)
        logger.info("Saved upload %s → %s (%d bytes)", upload_id, dest, total)
    except (InvalidCSV, UnsupportedFileType):
        raise
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise InvalidCSV(f"Could not save file: {exc}") from exc

    # ── 4. Parse CSV ──────────────────────────────────────────────────────
    try:
        df = load_csv(dest)
    except ValueError as exc:
        dest.unlink(missing_ok=True)
        raise InvalidCSV(str(exc)) from exc

    summary = dataframe_summary(df)

    # ── 5. Detect platform ────────────────────────────────────────────────
    detected = source or detect_platform(summary["columns"])

    return UploadResponse(
        upload_id=upload_id,
        filename=filename,
        rows=summary["rows"],
        columns=summary["columns"],
        column_count=summary["column_count"],
        platform_detected=detected,
        status="success",
        message=f"Uploaded {summary['rows']} rows × {summary['column_count']} columns.",
    )
