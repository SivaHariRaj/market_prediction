"""
Custom exception hierarchy for AIgnition backend.
All exceptions are FastAPI-compatible HTTPExceptions.
"""
from fastapi import HTTPException, status


class UploadNotFound(HTTPException):
    def __init__(self, upload_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload '{upload_id}' not found. Please upload a file first.",
        )


class InvalidCSV(HTTPException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV: {reason}",
        )


class UnsupportedFileType(HTTPException):
    def __init__(self, filename: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type for '{filename}'. Only .csv files are accepted.",
        )


class MLNotImplemented(HTTPException):
    def __init__(self, feature: str = "forecast"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"The ML model for '{feature}' is not yet implemented. "
                "Returning rule-based fallback data."
            ),
        )


class ReportGenerationError(HTTPException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {reason}",
        )


class ValidationError(HTTPException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {reason}",
        )
