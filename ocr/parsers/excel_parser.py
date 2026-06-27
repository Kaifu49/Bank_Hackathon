import pandas as pd

from services.tabular_reader import TabularReader


class ExcelParser:
    """
    Excel parser that does NOT assume row 0 is the header and scans all sheets.

    Like the CSV parser, real bank exports put metadata/title rows above the
    column header (yielding ``Unnamed: N``) or pipe everything into one column.
    We read each sheet as a raw grid (header=None) and let TabularReader find
    the header row or infer columns from values, keeping whichever sheet yields
    the most transaction rows.
    """

    def __init__(self):
        self.reader = TabularReader()

    def parse(self, file_path: str):
        sheets = pd.read_excel(
            file_path, header=None, dtype=str, sheet_name=None
        )

        best_rows = []
        best_meta = {"mode": "none"}
        best_sheet = None

        for name, df in sheets.items():
            df = df.fillna("")
            grid = self._expand_pipe_columns(df.values.tolist())
            rows, meta = self.reader.read_grid(grid)
            if len(rows) > len(best_rows):
                best_rows, best_meta, best_sheet = rows, meta, name

        if best_rows:
            return {
                "source_type": "excel",
                "rows": best_rows,
                "sheet": best_sheet,
                "table_resolution": best_meta,
            }

        # Fallback: legacy first-row-as-header on the first sheet.
        df2 = pd.read_excel(file_path, dtype=str).fillna("")
        return {
            "source_type": "excel",
            "rows": df2.to_dict(orient="records"),
            "table_resolution": {"mode": "legacy_header_row0"},
        }

    def _expand_pipe_columns(self, grid):
        """
        Some bank Excel exports cram the whole table into one pipe-delimited
        column (e.g. ``ACCOUNT | TRAN ID | ... | BALANCE``). If most rows are a
        single cell containing '|', split on '|' into real columns.
        """
        single_pipe = [
            r for r in grid
            if len(r) == 1 and isinstance(r[0], str) and "|" in r[0]
        ]
        if grid and len(single_pipe) >= max(1, len(grid) // 2):
            return [
                [c.strip() for c in str(r[0]).split("|")] if len(r) == 1 else r
                for r in grid
            ]
        return grid
