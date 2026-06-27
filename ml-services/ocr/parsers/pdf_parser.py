import pdfplumber


class PDFParser:

    def parse(
        self,
        file_path: str,
    ):

        text = []

        with pdfplumber.open(
            file_path
        ) as pdf:

            for page in pdf.pages:

                tables = page.extract_tables()

                print(
                    f"Found {len(tables)} tables"
                )
                page_text = (
                    page.extract_text()
                )

                if page_text:
                    text.append(
                        page_text
                    )

        return {
            "source_type": "pdf",
            "rows": text,
            "ocr_required":
                len(text) == 0
        }