"""
Report service (Phase 7 / Core Requirement 6).
Generates investigation reports as JSON / Excel / PDF / DOCX.
Run: uvicorn main:app --reload --port 8010
"""

import io

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse

from services.report_builder import ReportBuilder
from services.excel_report import build_excel
from services.docx_report import build_docx

app = FastAPI()
builder = ReportBuilder()


@app.get("/health")
def health():
    return {"service": "report", "status": "healthy"}


def _download(data: bytes, media_type: str, filename: str):
    return StreamingResponse(
        io.BytesIO(data),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/report/{case_id}/json")
def report_json(case_id: str, refresh: bool = False):
    return JSONResponse(builder.build(case_id, refresh=refresh))


@app.get("/report/{case_id}/excel")
def report_excel(case_id: str, refresh: bool = False):
    data = build_excel(builder.build(case_id, refresh=refresh))
    return _download(
        data,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        f"investigation_report_{case_id}.xlsx",
    )


@app.get("/report/{case_id}/docx")
def report_docx(case_id: str, refresh: bool = False):
    data = build_docx(builder.build(case_id, refresh=refresh))
    return _download(
        data,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        f"investigation_report_{case_id}.docx",
    )


@app.get("/report/{case_id}/pdf")
def report_pdf(case_id: str, refresh: bool = False):
    try:
        from services.pdf_report import build_pdf
        data = build_pdf(builder.build(case_id, refresh=refresh))
    except ImportError:
        return JSONResponse(
            status_code=501,
            content={"error": "reportlab not installed. Run: pip install reportlab"},
        )
    return _download(data, "application/pdf", f"investigation_report_{case_id}.pdf")
