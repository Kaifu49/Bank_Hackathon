import pandas as pd

from services.tabular_reader import TabularReader


class CSVParser:
    """
    CSV parser that does NOT assume row 0 is the header.

    Real bank CSVs frequently carry title/metadata rows above the column header
    (pandas would otherwise yield ``Unnamed: N`` columns), use tab instead of
    comma, or have no header at all. We read the raw grid (header=None,
    delimiter auto-detected) and let TabularReader find the header row or infer
    columns from values.
    """

    def __init__(self):
        self.reader = TabularReader()

    def parse(self, file_path: str):
        # sep=None + engine="python" auto-detects comma/tab/semicolon delimiters
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
                "source_type": "csv",
                "rows": rows,
                "table_resolution": meta,
            }

        # Fallback: legacy first-row-as-header behaviour.
        df2 = pd.read_csv(file_path, dtype=str).fillna("")
        return {
            "source_type": "csv",
            "rows": df2.to_dict(orient="records"),
            "table_resolution": {"mode": "legacy_header_row0"},
        }
