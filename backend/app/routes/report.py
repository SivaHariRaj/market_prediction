"""
GET /report
Download a CSV or PDF report.
"""
from fastapi import APIRouter, Query, status
from fastapi.responses import Response

from app.services.forecast_service import run_forecast
from app.services.optimizer_service import run_optimizer
from app.services.risk_service import run_risks
from app.services.summary_service import run_summary
from app.services.report_service import generate_csv_report, generate_pdf_report
from app.utils.exceptions import ReportGenerationError, UploadNotFound
from app.utils.file_utils import find_upload_file
from app.utils.logger import get_logger

router = APIRouter(prefix="/report", tags=["Report"])
logger = get_logger(__name__)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Download a CSV or PDF report",
    description=(
        "Generates a complete report from the latest forecast, optimizer, and risk data "
        "for the given `upload_id`. Pass `format=csv` or `format=pdf`."
    ),
    responses={
        200: {
            "content": {
                "text/csv": {},
                "application/pdf": {},
            },
            "description": "Downloadable report file.",
        }
    },
)
async def download_report(
    upload_id: str = Query(..., description="ID from POST /upload"),
    format: str = Query(default="pdf", description="Report format: csv | pdf"),
    total_budget: float = Query(default=420_000.0, description="Total budget for optimizer"),
) -> Response:
    # Verify upload exists
    if find_upload_file(upload_id) is None:
        raise UploadNotFound(upload_id)

    fmt = format.lower()
    if fmt not in ("csv", "pdf"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="format must be 'csv' or 'pdf'")

    try:
        # Gather all data
        forecast = run_forecast(upload_id)
        optimizer = run_optimizer(upload_id, total_budget=total_budget)
        risks_resp = run_risks(upload_id)
        summary = run_summary(
            upload_id,
            forecast=forecast.model_dump(),
            optimizer=optimizer.model_dump(),
            risks=[r.model_dump() for r in risks_resp.risks],
        )

        payload = {
            "upload_id": upload_id,
            "forecast": forecast.model_dump(),
            "optimizer": optimizer.model_dump(),
            "risks": [r.model_dump() for r in risks_resp.risks],
            "summary": summary.model_dump(),
        }

        if fmt == "csv":
            content = generate_csv_report(payload)
            return Response(
                content=content,
                media_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="aignition-report-{upload_id}.csv"'},
            )
        else:
            content = generate_pdf_report(payload)
            return Response(
                content=content,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="aignition-report-{upload_id}.pdf"'},
            )

    except (UploadNotFound, ReportGenerationError):
        raise
    except Exception as exc:
        logger.exception("Report generation failed for %s", upload_id)
        raise ReportGenerationError(str(exc)) from exc
