from pdf2image import convert_from_path

from services.ocr_service import (
    OCRService
)


class ScannedPDFParser:

    def __init__(self):

        self.ocr = OCRService()

    def parse(
        self,
        file_path: str,
    ):

        pages = convert_from_path(
            file_path
        )

        rows = []

        for index, page in enumerate(
            pages
        ):

            image_path = (
                f"temp_page_{index}.png"
            )

            page.save(
                image_path,
                "PNG"
            )

            text = (
                self.ocr.extract_text(
                    image_path
                )
            )

            rows.extend(text)

        return {
            "source_type":
                "scanned_pdf",
            "rows": rows
        }