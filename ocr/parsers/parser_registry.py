from pathlib import Path

from parsers.pdf_parser import PDFParser
from parsers.csv_parser import CSVParser
from parsers.excel_parser import ExcelParser
from parsers.docx_parser import DOCXParser
from parsers.image_parser import ImageParser
from parsers.txt_parser import TXTParser


class ParserRegistry:

    def __init__(self):

        self.parsers = {
            ".pdf": PDFParser(),
            ".csv": CSVParser(),

            ".xlsx": ExcelParser(),
            ".xls": ExcelParser(),

            ".docx": DOCXParser(),

            ".txt": TXTParser(),

            ".png": ImageParser(),
            ".jpg": ImageParser(),
            ".jpeg": ImageParser(),
        }

    def get_parser(
        self,
        file_path: str,
    ):

        extension = (
            Path(file_path)
            .suffix
            .lower()
        )

        parser = self.parsers.get(
            extension
        )

        if parser is None:

            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        return parser