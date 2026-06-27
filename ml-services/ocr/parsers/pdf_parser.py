import pdfplumber

from services.pdf_table_extractor import PdfTableExtractor


class PDFParser:
    """
    Text-based PDF parser with a table-first strategy:

      1. Try `extract_tables()` per page. If a confident transaction table is
         found, emit structured dict rows directly (cleanest path) and carry the
         header across pages for headerless continuations.
      2. Otherwise return the raw page text; ExtractionService then runs the
         TextStatementReconstructor to recover rows from messy layouts.

    Either way the result also carries `raw_text` for debugging/audit.
    """

    def __init__(self):
        self.table_extractor = PdfTableExtractor()

    def parse(self, file_path: str):
        text_pages = []
        table_rows = []
        carry_header = None

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # text (always collected, for fallback + audit)
                page_text = page.extract_text()
                if page_text:
                    text_pages.append(page_text)

                # tables (preferred when they describe transactions)
                try:
                    tables = page.extract_tables() or []
                except Exception as exc:  # malformed table geometry
                    print(f"[WARN] extract_tables failed on a page: {exc}")
                    tables = []

                for table in tables:
                    rows, carry_header = self.table_extractor.process_table(
                        table, carry_header
                    )
                    table_rows.extend(rows)

        # Prefer structured table rows when we recovered a meaningful number.
        if len(table_rows) >= 1:
            print(
                f"[INFO] PDF table path: {len(table_rows)} structured rows."
            )
            return {
                "source_type": "pdf",
                "rows": table_rows,
                "extraction": "tables",
                "raw_text": text_pages,
                "ocr_required": False,
            }

        # Fall back to raw text (reconstructed downstream), or OCR if empty.
        return {
            "source_type": "pdf",
            "rows": text_pages,
            "extraction": "text",
            "ocr_required": len(text_pages) == 0,
        }
