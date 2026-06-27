import re


DATE_PATTERN = re.compile(
    r"\d{1,2}\s?[A-Za-z]{3}"
)


class TransactionMerger:

    def merge(
        self,
        rows
    ):

        merged = []

        current = None

        for row in rows:

            row_text = " ".join(row)

            has_date = (
                DATE_PATTERN.search(
                    row_text
                )
                is not None
            )

            if has_date:

                if current:
                    merged.append(
                        current
                    )

                current = row.copy()

            else:

                if current:

                    current.extend(
                        row
                    )

        if current:
            merged.append(
                current
            )

        return merged