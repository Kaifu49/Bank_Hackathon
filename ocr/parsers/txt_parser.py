from services.tabular_reader import TabularReader
from services import delimited_reader


class TXTParser:
    """
    Plain-text statement parser. TXT files in the dataset are either delimited
    tables (tab/comma/pipe) or free-text statements.

      * First read as a ragged-tolerant delimited grid -> TabularReader (header
        detection or content inference).
      * If that yields nothing, return the raw text; ExtractionService then runs
        the TextStatementReconstructor (balance-delta) on it.
    """

    def __init__(self):
        self.reader = TabularReader()

    def parse(self, file_path: str):
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()

        try:
            grid = delimited_reader.read_grid(file_path)
            rows, meta = self.reader.read_grid(grid)
            if rows:
                return {
                    "source_type": "txt",
                    "rows": rows,
                    "table_resolution": meta,
                }
        except Exception as exc:
            print(f"[WARN] TXT delimited read failed, using text path: {exc}")

        # Free-text fallback: reconstructed downstream by ExtractionService.
        return {
            "source_type": "txt",
            "rows": [text],
            "extraction": "text",
            "ocr_required": len(text.strip()) == 0,
        }
