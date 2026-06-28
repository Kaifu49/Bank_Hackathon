"""
Render the report data model to a PDF (Core Requirement 6, graded).

Uses reportlab (pip install reportlab). Kept dependency-isolated: the import is
inside build_pdf so the rest of the report service runs even if reportlab isn't
installed yet (the endpoint then returns a clear error).
"""

import io


def build_pdf(report: dict) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    )

    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm)
    flow = []

    def table(headers, rows):
        data = [headers] + [["" if c is None else str(c) for c in r] for r in rows]
        t = Table(data, repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FB")]),
        ]))
        return t

    flow.append(Paragraph(report.get("title", "Investigation Report"), title_style))
    flow.append(Paragraph(f"Case: {report.get('case_id', 'all')}", body))
    flow.append(Spacer(1, 8))

    # Executive summary
    flow.append(Paragraph("Executive Summary", h1))
    es = report.get("executive_summary", {})
    flow.append(table(
        ["Metric", "Value"],
        [[k.replace("_", " ").title(), v] for k, v in es.items()],
    ))
    flow.append(Spacer(1, 10))

    # Top risks
    flow.append(Paragraph("Top Suspicious Accounts", h2))
    flow.append(table(
        ["Account", "Risk", "Level", "Patterns"],
        [[r.get("node") or r.get("account"), r.get("risk_score"), r.get("risk_level"),
          "; ".join(r.get("patterns", []) or r.get("top_reasons", []) or [])]
         for r in report.get("top_risks", [])[:15]],
    ))
    flow.append(Spacer(1, 10))

    # Round trips
    flow.append(Paragraph("Round-Trip / Circular Flows", h2))
    flow.append(table(
        ["Chain", "Path", "Bottleneck", "Total"],
        [[c.get("id"), " -> ".join(c.get("nodes", [])), c.get("min_amount"),
          c.get("total_amount")]
         for c in report.get("round_trips", [])[:15]],
    ))
    flow.append(Spacer(1, 10))

    # Money flow
    flow.append(Paragraph("Money Flow", h2))
    mf = report.get("money_flow", {})
    flow.append(Paragraph(f"Destination account: {mf.get('destination_account')}", body))
    flow.append(table(
        ["Accumulation Account", "Total Received", "Senders"],
        [[a.get("node"), a.get("total_received"), a.get("sender_count")]
         for a in mf.get("accumulation_accounts", [])[:10]],
    ))
    flow.append(Spacer(1, 10))

    # Recommendations
    flow.append(Paragraph("Recommendations", h2))
    for rec in report.get("recommendations", []):
        flow.append(Paragraph(f"• {rec}", body))

    doc.build(flow)
    return buf.getvalue()
