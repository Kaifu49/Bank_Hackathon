"""
PdfTableExtractor — turns pdfplumber `extract_tables()` output into structured
transaction dict rows, when the PDF actually has a real grid table.

It is deliberately *pdfplumber-independent*: it consumes the plain nested-list
shape pdfplumber returns (``list[table]`` where ``table = list[row]`` and
``row = list[cell|None]``). That keeps it unit-testable without the heavy PDF
stack and keeps the parser thin.

Strategy (bank/layout agnostic):
  * Identify a *transaction header* row by keyword evidence: it must look like a
    date column AND at least one money column (debit/credit/withdrawal/deposit/
    amount/balance). Metadata tables (account info, summaries) fail this test.
  * Build dict rows {header_cell: value} from the rows beneath the header.
  * Carry the established header across pages so headerless continuation tables
    (very common — header printed once) are still parsed, as long as the column
    count matches and the row carries transaction-like content (a date/money).
  * Drop repeated header rows, blank rows, and sub-header fragments.

Returns [] when no confident transaction table is present, so the caller can
fall back to the text reconstructor.
"""

from __future__ import annotations

import re
from typing import Optional


_DATE_HDR = re.compile(r"\b(date|dt)\b", re.I)
_MONEY_HDR = {
    "debit", "debits", "dr", "credit", "credits", "cr",
    "withdrawal", "withdrawals", "deposit", "deposits",
    "balance", "bal", "amount", "amt",
}
_NARR_HDR = {"description", "narration", "particulars", "particular",
             "details", "remarks"}

_DATE_VAL = re.compile(
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}[/-][A-Za-z]{3}[/-]\d{2,4})\b"
)
_MONEY_VAL = re.compile(r"\d{1,3}(?:,\d{3})*\.\d{2}|\d+\.\d{2}")


def _clean(cell) -> str:
    if cell is None:
        return ""
    return re.sub(r"\s+", " ", str(cell).replace("\n", " ")).strip()


def _norm(cell) -> str:
    return re.sub(r"[._/\\\-():*'\"`]", " ", _clean(cell).lower()).strip()


class PdfTableExtractor:

    def is_transaction_header(self, row: list) -> bool:
        cells = [_norm(c) for c in row]
        joined = " ".join(cells)
        has_date = bool(_DATE_HDR.search(joined))
        has_money = any(
            any(tok == w or tok in w.split() for w in _MONEY_HDR)
            for c in cells for tok in c.split()
        ) or any(m in joined for m in _MONEY_HDR)
        # Require a date-ish header + a money-ish header, and >=3 labelled cols.
        labelled = sum(1 for c in cells if c)
        return has_date and has_money and labelled >= 3

    def _is_data_row(self, row: list, ncols: int) -> bool:
        cells = [_clean(c) for c in row]
        if not any(cells):
            return False
        text = " ".join(cells)
        return bool(_DATE_VAL.search(text) or _MONEY_VAL.search(text))

    def _row_to_dict(self, header: list, row: list) -> dict:
        out = {}
        for i, h in enumerate(header):
            key = _clean(h) or f"col_{i}"
            val = _clean(row[i]) if i < len(row) else ""
            out[key] = val if val != "" else None
        return out

    def process_table(self, table: list, carry_header: Optional[list]):
        """
        Process one table. Returns (rows, header_to_carry).
        `carry_header` is the transaction header established on a previous page.
        """
        rows: list[dict] = []
        if not table:
            return rows, carry_header

        # Find the header row inside this table (if any).
        header_idx = None
        for i, r in enumerate(table):
            if self.is_transaction_header(r):
                header_idx = i
                break

        if header_idx is not None:
            header = [_clean(c) for c in table[header_idx]]
            data_rows = table[header_idx + 1:]
        elif carry_header is not None and self._matches_width(table, carry_header):
            header = carry_header
            data_rows = table
        else:
            return rows, carry_header  # not a transaction table

        norm_header = [_norm(c) for c in header]
        ncols = len(header)
        for r in data_rows:
            if self._is_header_repeat(r, norm_header):
                continue
            if not self._is_data_row(r, ncols):
                continue
            rows.append(self._row_to_dict(header, r))

        return rows, header

    def _matches_width(self, table: list, header: list) -> bool:
        widths = [len(r) for r in table if any(_clean(c) for c in r)]
        if not widths:
            return False
        # majority of rows share the header's column count
        same = sum(1 for w in widths if w == len(header))
        return same >= max(1, len(widths) // 2)

    def _is_header_repeat(self, row: list, norm_header: list) -> bool:
        return [_norm(c) for c in row] == norm_header
