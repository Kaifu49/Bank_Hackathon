"""
TabularReader — turn a raw 2-D grid (from CSV/XLS/XLSX/TXT, read WITHOUT
assuming row 0 is the header) into structured transaction dict rows.

Two strategies, tried in order:
  1. Header detection — reuse PdfTableExtractor to find a real transaction
     header row anywhere in the grid (handles metadata/title rows above it).
  2. Content inference — if no header row exists (pandas produced ``Unnamed: N``
     and the values themselves carry the structure), profile columns by value
     and assign canonical fields, disambiguating debit/credit by balance delta.

Returns (rows, meta). rows == [] means "this grid is not a parseable table"
so the caller can fall back to text reconstruction (important for free-text
TXT files).
"""

from __future__ import annotations

from services.pdf_table_extractor import PdfTableExtractor
from services.content_column_profiler import ContentColumnProfiler


class TabularReader:

    def __init__(self):
        self.table_extractor = PdfTableExtractor()
        self.profiler = ContentColumnProfiler()

    def read_grid(self, grid: list[list]):
        if not grid:
            return [], {"mode": "empty"}

        # 1) header-row detection
        rows, header = self.table_extractor.process_table(grid, None)
        if rows:
            return rows, {"mode": "header_detected", "header": header}

        # 2) content-based inference
        result = self.profiler.infer(grid)
        if result["rows"]:
            return result["rows"], {
                "mode": "content_inferred",
                "assignment": result["assignment"],
            }

        return [], {"mode": "unparsed", "reason": result.get("reason")}
