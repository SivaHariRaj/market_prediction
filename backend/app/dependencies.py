"""
AIgnition Backend — FastAPI Dependencies
"""
from fastapi import Header, HTTPException, status
from typing import Optional

from app.utils.file_utils import find_upload_file
from app.utils.exceptions import UploadNotFound


async def get_upload_or_404(upload_id: str) -> str:
    """
    Dependency that verifies an upload_id exists on disk.
    Raises 404 if the file cannot be found.
    """
    path = find_upload_file(upload_id)
    if path is None:
        raise UploadNotFound(upload_id)
    return upload_id


async def optional_request_id(
    x_request_id: Optional[str] = Header(default=None),
) -> Optional[str]:
    """Pass-through X-Request-ID header for tracing."""
    return x_request_id
