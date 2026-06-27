from services.tabular_reader import TabularReader
from services import delimited_reader


class CSVParser:
    """
    CSV parser that does NOT assume row 0 is the header and tolerates ragged
    rows (metadata preambles with a different delimiter count than the data
    rows, which crash pandas with "Expected N fields ... saw M").

    Reads the raw grid via the csv module (delimiter auto-detected, comma/tab/
    pipe/semicolon), then lets TabularReader find the header row or infer
    columns from values.
    """

    def __init__(self):
        self.reader = TabularReader()

    def parse(self, file_path: str):
        grid = delimited_reader.read_grid(file_path)
        rows, meta = self.reader.read_grid(grid)

        if rows:
            return {
                "source_type": "csv",
                "rows": rows,
                "table_resolution": meta,
            }

        # Last resort: emit the raw text so ExtractionService can reconstruct.
        text = "\n".join("\t".join(r) for r in grid)
        return {
            "source_type": "csv",
            "rows": [text] if text.strip() else [],
            "extraction": "text",
            "table_resolution": {"mode": "fallback_text"},
        }
