from parsers.parser_registry import ParserRegistry
from parsers.scanned_pdf_parser import ScannedPDFParser
from services.text_statement_reconstructor import (
    TextStatementReconstructor,
)


class ExtractionService:

    def __init__(self):

        self.registry = ParserRegistry()
        self.scanned_pdf_parser = ScannedPDFParser()
        self.text_reconstructor = TextStatementReconstructor()

    def extract(
        self,
        file_path: str,
    ):

        parser = self.registry.get_parser(
            file_path
        )

        result = parser.parse(
            file_path
        )

        # Handle scanned PDFs
        if (
            result.get("source_type") == "pdf"
            and result.get("ocr_required", False)
        ):

            print(
                f"[INFO] No extractable text found in {file_path}. "
                "Switching to OCR pipeline..."
            )

            result = self.scanned_pdf_parser.parse(
                file_path
            )

        # Normalize the `rows` contract: every downstream consumer expects
        # list[dict]. Text-based PDFs (and OCR'd scans) emit list[str] page
        # text -> reconstruct into structured transaction dict rows so the
        # standardize service never receives bare strings (the 422 bug).
        result = self._ensure_structured_rows(result)

        return result

    def _ensure_structured_rows(self, result: dict) -> dict:
        rows = result.get("rows")
        if not isinstance(rows, list) or not rows:
            return result

        # Already structured (CSV/Excel parsers) -> leave as-is.
        if all(isinstance(r, dict) for r in rows):
            return result

        # Page-text strings -> reconstruct.
        text_pages = [r for r in rows if isinstance(r, str)]
        if not text_pages:
            return result

        structured = self.text_reconstructor.reconstruct(text_pages)
        result["raw_text"] = text_pages          # keep original for debugging
        result["rows"] = structured
        result["row_reconstruction"] = "text_statement_reconstructor"
        print(
            f"[INFO] Reconstructed {len(structured)} transaction rows "
            f"from {len(text_pages)} text page(s)."
        )
        return result