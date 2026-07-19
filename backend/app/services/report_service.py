"""
AIgnition — Report Service
Generates CSV and PDF reports from structured forecast/optimizer/risk data.
"""
import csv
import io
from datetime import datetime
from typing import Any

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# CSV
# ──────────────────────────────────────────────────────────────────────────────

def generate_csv_report(data: dict[str, Any]) -> bytes:
    """
    Build a multi-section CSV report from the unified dashboard data.
    Returns raw bytes ready to stream.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    _write_header(writer, data)
    _write_section(writer, "REVENUE FORECAST", _flatten_forecast(data))
    _write_section(writer, "BUDGET OPTIMIZER", _flatten_optimizer(data))
    _write_section(writer, "RISK SIGNALS", _flatten_risks(data))
    _write_section(writer, "EXECUTIVE SUMMARY", _flatten_summary(data))

    return output.getvalue().encode("utf-8-sig")  # BOM for Excel compatibility


def _write_header(writer: csv.writer, data: dict) -> None:
    writer.writerow([f"{settings.REPORT_COMPANY_NAME} · AI Marketing Decision Report"])
    writer.writerow(["Generated", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")])
    writer.writerow(["Upload ID", data.get("upload_id", "N/A")])
    writer.writerow([])


def _write_section(writer: csv.writer, title: str, rows: list[list]) -> None:
    writer.writerow([title])
    for row in rows:
        writer.writerow(row)
    writer.writerow([])


def _flatten_forecast(data: dict) -> list[list]:
    f = data.get("forecast", {})
    rf = f.get("revenue_forecast", {}) if isinstance(f, dict) else {}
    roas = f.get("roas_forecast", {}) if isinstance(f, dict) else {}
    return [
        ["Metric", "Value"],
        ["Expected Revenue", f"${rf.get('expected', 0):,.0f}"],
        ["Uplift vs Baseline", f"+{rf.get('uplift_pct', 0):.1f}%"],
        ["P10 Revenue", f"${rf.get('p10', 0):,.0f}"],
        ["P50 Revenue", f"${rf.get('p50', 0):,.0f}"],
        ["P90 Revenue", f"${rf.get('p90', 0):,.0f}"],
        ["Expected ROAS", f"{roas.get('expected', 0):.2f}x"],
        ["Confidence", f"{rf.get('confidence', 0):.0f}%"],
        ["MAPE", f"{rf.get('mape', 0):.1f}%"],
    ]


def _flatten_optimizer(data: dict) -> list[list]:
    opt = data.get("optimizer", {})
    if not isinstance(opt, dict):
        return []
    rows = [
        ["Channel", "Current %", "Optimized %", "Budget ($)", "ROAS"],
    ]
    for ch in opt.get("channels", []):
        if isinstance(ch, dict):
            rows.append([
                ch.get("channel", ""),
                f"{ch.get('current_pct', 0):.1f}%",
                f"{ch.get('optimized_pct', 0):.1f}%",
                f"${ch.get('optimized_budget', 0):,.0f}",
                f"{ch.get('roas', 0):.2f}x",
            ])
    rows.append(["Expected Revenue", f"${opt.get('expected_revenue', 0):,.0f}"])
    rows.append(["Estimated Uplift", f"+{opt.get('estimated_uplift_pct', 0):.1f}%"])
    return rows


def _flatten_risks(data: dict) -> list[list]:
    risks = data.get("risks", [])
    if not risks:
        return [["No risks detected."]]
    rows = [["ID", "Title", "Severity", "Description", "Signal"]]
    for r in risks:
        if isinstance(r, dict):
            rows.append([
                r.get("id", ""),
                r.get("title", ""),
                r.get("severity", ""),
                r.get("description", ""),
                r.get("metric", ""),
            ])
    return rows


def _flatten_summary(data: dict) -> list[list]:
    s = data.get("summary", {})
    if not isinstance(s, dict):
        return []
    rows = [["Executive Summary", s.get("executive_summary", "")], []]
    recs = s.get("recommendations", [])
    if recs:
        rows.append(["Recommendations"])
        for rec in recs:
            rows.append(["", rec])
    drivers = s.get("key_drivers", [])
    if drivers:
        rows.append([])
        rows.append(["Key Drivers"])
        for d in drivers:
            rows.append(["", d])
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# PDF
# ──────────────────────────────────────────────────────────────────────────────

def generate_pdf_report(data: dict[str, Any]) -> bytes:
    """
    Generate a PDF report using reportlab.
    Returns raw bytes ready to stream.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
        )
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
    except ImportError:
        logger.error("reportlab not installed — cannot generate PDF")
        raise RuntimeError(
            "reportlab is required for PDF generation. Install it via: pip install reportlab"
        )

    buffer = io.BytesIO()
    PAGE_W, PAGE_H = A4
    BRAND = colors.HexColor("#6366f1")
    BRAND_LIGHT = colors.HexColor("#eef2ff")
    SUCCESS = colors.HexColor("#22c55e")
    WARNING = colors.HexColor("#f59e0b")
    DANGER = colors.HexColor("#ef4444")
    MUTED = colors.HexColor("#64748b")

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    style_h1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=colors.HexColor("#1e293b"), fontSize=20, spaceAfter=4)
    style_h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=BRAND, fontSize=12, spaceBefore=12, spaceAfter=4)
    style_body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#334155"), leading=14)
    style_muted = ParagraphStyle("Muted", parent=styles["Normal"], fontSize=8, textColor=MUTED, leading=12)
    style_label = ParagraphStyle("Label", parent=styles["Normal"], fontSize=7, textColor=MUTED, fontName="Helvetica-Bold")

    story = []

    # ── Header ─────────────────────────────────────────────────────────────
    story.append(Paragraph(f"<font color='#{BRAND.hexval()[2:]}'>AIgnition</font> · Marketing Decision Report", style_h1))
    story.append(Paragraph(
        f"Generated {datetime.utcnow().strftime('%B %d, %Y')} · Upload ID: {data.get('upload_id', 'N/A')}",
        style_muted,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=BRAND, spaceAfter=8))

    # ── KPI Block ──────────────────────────────────────────────────────────
    f = data.get("forecast", {})
    rf = f.get("revenue_forecast", {}) if isinstance(f, dict) else {}
    roas_f = f.get("roas_forecast", {}) if isinstance(f, dict) else {}

    kpi_data = [
        ["EXPECTED REVENUE", "BLENDED ROAS", "CONFIDENCE"],
        [
            f"${rf.get('expected', 0):,.0f}",
            f"{roas_f.get('expected', 0):.2f}x",
            f"{rf.get('confidence', 0):.0f}%",
        ],
        [
            f"+{rf.get('uplift_pct', 0):.1f}% vs baseline",
            "next 30 days",
            f"MAPE {rf.get('mape', 0):.1f}%",
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[(PAGE_W - 40 * mm) / 3] * 3)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, 0), BRAND),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("FONTSIZE", (0, 1), (-1, 1), 16),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 2), (-1, 2), 8),
        ("TEXTCOLOR", (0, 2), (-1, 2), SUCCESS),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BRAND_LIGHT, colors.white, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 8 * mm))

    # ── Optimizer table ────────────────────────────────────────────────────
    story.append(Paragraph("Budget Allocation", style_h2))
    opt = data.get("optimizer", {})
    channels = opt.get("channels", []) if isinstance(opt, dict) else []
    if channels:
        ch_data = [["CHANNEL", "CURRENT %", "OPTIMIZED %", "BUDGET", "ROAS"]]
        for ch in channels:
            if isinstance(ch, dict):
                delta = ch.get("delta_pct", 0)
                ch_data.append([
                    ch.get("channel", ""),
                    f"{ch.get('current_pct', 0):.1f}%",
                    f"{ch.get('optimized_pct', 0):.1f}%",
                    f"${ch.get('optimized_budget', 0):,.0f}",
                    f"{ch.get('roas', 0):.2f}x",
                ])
        ch_table = Table(ch_data, colWidths=[55*mm, 30*mm, 35*mm, 35*mm, 30*mm])
        ch_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(ch_table)
    story.append(Spacer(1, 6 * mm))

    # ── Risks ──────────────────────────────────────────────────────────────
    story.append(Paragraph("Risk Signals", style_h2))
    risks = data.get("risks", [])
    sev_color = {"risk": DANGER, "watch": WARNING, "healthy": SUCCESS}
    for r in risks:
        if not isinstance(r, dict):
            continue
        sev = r.get("severity", "watch")
        col = sev_color.get(sev, MUTED)
        story.append(Paragraph(
            f"<font color='#{col.hexval()[2:]}'><b>[{sev.upper()}]</b></font> "
            f"<b>{r.get('title', '')}</b> — {r.get('description', '')} "
            f"<font color='#94a3b8'>({r.get('metric', '')})</font>",
            style_body,
        ))
    story.append(Spacer(1, 6 * mm))

    # ── Executive Summary ──────────────────────────────────────────────────
    s = data.get("summary", {})
    if isinstance(s, dict) and s.get("executive_summary"):
        story.append(Paragraph("Executive Summary", style_h2))
        story.append(Paragraph(s["executive_summary"], style_body))
        story.append(Spacer(1, 4 * mm))
        recs = s.get("recommendations", [])
        if recs:
            story.append(Paragraph("Recommendations", style_label))
            for rec in recs:
                story.append(Paragraph(f"• {rec}", style_body))

    # ── Footer (first page only, via onFirstPage) ──────────────────────────
    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(
            20 * mm,
            12 * mm,
            f"{settings.REPORT_COMPANY_NAME} · AI Marketing Decision Copilot · {datetime.utcnow().year}",
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()
