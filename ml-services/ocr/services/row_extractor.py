import re


DATE_PATTERN = re.compile(
    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
)


class RowExtractor:

    def extract_rows(
        self,
        rows: list[str],
        start_index: int
    ):

        transactions = []

        for row in rows[start_index + 1:]:

            if DATE_PATTERN.search(row):

                transactions.append(
                    row
                )

        return transactions