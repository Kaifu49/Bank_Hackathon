from parsers.parser_registry import ParserRegistry
from parsers.scanned_pdf_parser import ScannedPDFParser


class ExtractionService:

    def __init__(self):

        self.registry = ParserRegistry()
        self.scanned_pdf_parser = ScannedPDFParser()

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

        return result