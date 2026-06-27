from docx import Document


class DOCXParser:

    def parse(self, file_path: str):

        doc = Document(file_path)

        paragraphs = [
            p.text
            for p in doc.paragraphs
            if p.text.strip()
        ]

        return {
            "source_type": "docx",
            "rows": paragraphs
        }