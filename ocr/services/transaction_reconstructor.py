import re


DATE_PATTERN = re.compile(
    r"\d{1,2}\s?[A-Za-z]{3}\s?\d{2,4}"
)

AMOUNT_PATTERN = re.compile(
    r"^\d[\d,]*\.\d{2}$"
)


class TransactionReconstructor:

    def reconstruct(
        self,
        rows: list[str]
    ):

        transactions = []

        current = []

        for row in rows:

            row = row.strip()

            if not row:
                continue

            if DATE_PATTERN.search(row):

                if current:
                    transactions.append(
                        current
                    )

                current = [row]

            else:

                current.append(row)

        if current:
            transactions.append(current)

        return transactions