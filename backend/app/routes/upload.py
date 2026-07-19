"""
POST /upload
Accept a CSV file and return parsed metadata.
"""
from typing import Optional
from fastapi import APIRouter, File, Form, UploadFile, status

from app.models.response_models import UploadResponse
from app.services.upload_service import handle_upload

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a marketing CSV",
    description=(
        "Accepts a CSV file from Google Ads, Meta Ads, Microsoft Ads, GA4, or Shopify. "
        "Returns an `upload_id` that is required by all downstream endpoints."
    ),
)
async def upload_csv(
    file: UploadFile = File(..., description="Marketing CSV file"),
    source: Optional[str] = Form(
        default=None,
        description="Ad platform hint: google_ads | meta_ads | microsoft_ads | ga4 | shopify",
    ),
) -> UploadResponse:
    return await handle_upload(file, source=source)
