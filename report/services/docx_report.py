"""Render the report data model to a .docx document."""

import io
from docx import Document
from docx.shared import Pt


def _heading(doc, text, level=1):
    doc.add_heading(text, level=level)


def _kv_table(doc, data: dict):
    table = doc.add_table(rows=0, cols=2)
    table.style = "Light Grid Accent 1"
    for k, v in data.items():
        row = table.add_row().cells
        row[0].text = str(k).replace("_", " ").title()
        row[1].text = str(v)


def _table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = str(h)
    for r in rows:
        cells = table.add_row().cells
        for i, val in enumerate(r):
            cells[i].text = "" if val is None else str(val)


def build_docx(report: dict) -> bytes:
    doc = Document()
    doc.add_heading(report.get("title", "Investigation Report"), level=0)
    doc.add_paragraph(f"Case: {report.get('case_id', 'all')}")

    _heading(doc, "Executive Summary")
    _kv_table(doc, report.get("executive_summary", {}))

    _heading(doc, "Top Suspicious Accounts")
    _table(
        doc,
        ["Account", "Risk", "Level", "Patterns"],
        [
            [r.get("node") or r.get("account"), r.get("risk_score"),
             r.get("risk_level"),
             "; ".join(r.get("patterns", []) or r.get("top_reasons", []) or [])]
            for r in report.get("top_risks", [])[:15]
        ],
    )

    _heading(doc, "Round-Trip / Circular Flows")
    _table(
        doc,
        ["Chain", "Path", "Bottleneck", "Total"],
        [
            [c.get("id"), " -> ".join(c.get("nodes", [])),
             c.get("min_amount"), c.get("total_amount")]
            for c in report.get("round_trips", [])[:15]
        ],
    )

    _heading(doc, "Money Flow")
    mf = report.get("money_flow", {})
    doc.add_paragraph(f"Destination account: {mf.get('destination_account')}")
    _table(
        doc,
        ["Accumulation Account", "Total Received", "Senders"],
        [[a.get("node"), a.get("total_received"), a.get("sender_count")]
         for a in mf.get("accumulation_accounts", [])[:10]],
    )

    _heading(doc, "Recommendations")
    for rec in report.get("recommendations", []):
        p = doc.add_paragraph(style="List Bullet")
        run = p.add_run(rec)
        run.font.size = Pt(11)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
