from services.ocr_service import (
    OCRService
)


class ImageParser:

    def __init__(self):

        self.ocr = OCRService()

    def parse(
        self,
        file_path: str,
    ):

        lines = (
            self.ocr.extract_text(
                file_path
            )
        )

        return {
            "source_type": "image",
            "rows": lines
        }