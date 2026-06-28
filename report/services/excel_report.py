"""Render the report data model to an .xlsx workbook (Core Requirement 6)."""

import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

_HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
_HEADER_FONT = Font(bold=True, color="FFFFFF")
_TITLE_FONT = Font(bold=True, size=14)


def _sheet(wb, title):
    ws = wb.create_sheet(title=title[:31])
    return ws


def _header_row(ws, headers, row=1):
    for col, h in enumerate(headers, start=1):
        c = ws.cell(row=row, column=col, value=h)
        c.font = _HEADER_FONT
        c.fill = _HEADER_FILL


def _autosize(ws):
    for col in ws.columns:
        width = max((len(str(c.value)) for c in col if c.value is not None), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(60, width + 2)


def build_excel(report: dict) -> bytes:
    wb = Workbook()
    wb.remove(wb.active)  # drop default sheet

    # --- Summary ---
    ws = _sheet(wb, "Summary")
    ws["A1"] = report.get("title", "Investigation Report")
    ws["A1"].font = _TITLE_FONT
    es = report.get("executive_summary", {})
    ws.append([])
    _header_row(ws, ["Metric", "Value"], row=3)
    r = 4
    for k, v in es.items():
        ws.cell(row=r, column=1, value=k.replace("_", " ").title())
        ws.cell(row=r, column=2, value=v)
        r += 1
    _autosize(ws)

    # --- Top Risks ---
    ws = _sheet(wb, "Top Risks")
    _header_row(ws, ["Account", "Risk Score", "Risk Level", "Patterns"])
    for r in report.get("top_risks", []):
        ws.append([
            r.get("node") or r.get("account"),
            r.get("risk_score"),
            r.get("risk_level"),
            "; ".join(r.get("patterns", []) or r.get("top_reasons", []) or []),
        ])
    _autosize(ws)

    # --- Round Trips ---
    ws = _sheet(wb, "Round Trips")
    _header_row(ws, ["Chain ID", "Path", "Length", "Bottleneck", "Total"])
    for c in report.get("round_trips", []):
        ws.append([
            c.get("id"),
            " -> ".join(c.get("nodes", [])),
            c.get("length"),
            c.get("min_amount"),
            c.get("total_amount"),
        ])
    _autosize(ws)

    # --- Money Flow ---
    ws = _sheet(wb, "Money Flow")
    mf = report.get("money_flow", {})
    ws.append(["Destination account", mf.get("destination_account")])
    ws.append([])
    ws.append(["Accumulation accounts"])
    _header_row(ws, ["Account", "Total Received", "Sender Count"], row=ws.max_row + 1)
    for a in mf.get("accumulation_accounts", []):
        ws.append([a.get("node"), a.get("total_received"), a.get("sender_count")])
    ws.append([])
    ws.append(["Source accounts"])
    _header_row(ws, ["Account", "Total Sent", "Receiver Count"], row=ws.max_row + 1)
    for a in mf.get("source_accounts", []):
        ws.append([a.get("node"), a.get("total_sent"), a.get("receiver_count")])
    _autosize(ws)

    # --- Entities ---
    ws = _sheet(wb, "Entities")
    _header_row(ws, ["Type", "Identifier", "Display Name"])
    for e in report.get("top_entities", []):
        ws.append([e.get("entity_type"), e.get("identifier"), e.get("display_name")])
    _autosize(ws)

    # --- Recommendations ---
    ws = _sheet(wb, "Recommendations")
    _header_row(ws, ["#", "Recommendation"])
    for i, rec in enumerate(report.get("recommendations", []), start=1):
        ws.append([i, rec])
    _autosize(ws)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
