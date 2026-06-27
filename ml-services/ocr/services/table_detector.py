TABLE_KEYWORDS = {
    "date",
    "txn",
    "description",
    "narration",
    "particulars",
    "remarks",
    "debit",
    "credit",
    "withdrawal",
    "deposit",
    "balance",
    "ref"
}


class TableDetector:

    def find_table_start(
        self,
        rows: list[str]
    ):

        for i in range(len(rows)):

            score = 0

            window = rows[i:i+8]

            for row in window:

                row_lower = row.lower()

                for keyword in TABLE_KEYWORDS:

                    if keyword in row_lower:
                        score += 1

            if score >= 5:
                return i

        return None