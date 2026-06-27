import pandas as pd


class ExcelParser:

    def parse(self, file_path: str):

        df = pd.read_excel(file_path,dtype=str)

        df = df.fillna("")

        return {
            "source_type": "excel",
            "rows": df.to_dict(
                orient="records"
            )
        }