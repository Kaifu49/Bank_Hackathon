import re


class HeaderDetector:

    def detect(
        self,
        header_row: str
    ):

        columns = re.split(
            r"\s{2,}",
            header_row.strip()
        )

        return {
            column: idx
            for idx, column
            in enumerate(columns)
        }