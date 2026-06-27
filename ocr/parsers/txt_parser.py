import pandas as pd

from services.tabular_reader import TabularReader


class TXTParser:
    """
    Plain-text statement parser. TXT files in the dataset are either
    delimited tables (tab/comma/pipe) or free-text statements.

      * First try to read as a delimited grid -> TabularReader (header detect
        or content inference).
      * If that yields nothing, return the raw text; ExtractionService then runs
        the TextStatementReconstructor (balance-delta) on it.
    """

    def __init__(self):
        self.reader = TabularReader()

    def parse(self, file_path: str):
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()

        try:
            df = pd.read_csv(
                file_path,
                header=None,
                dtype=str,
                sep=None,
                engine="python",
                skip_blank_lines=False,
            ).fillna("")
            grid = df.values.tolist()
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
