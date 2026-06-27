import re


AMOUNT_PATTERN = re.compile(
    r"^\d[\d,]*\.\d{2}$"
)


class TransactionNormalizer:

    def normalize(
        self,
        transaction
    ):

        result = {
            "date": None,
            "description": "",
            "reference": None,
            "debit": None,
            "credit": None,
            "balance": None
        }

        if not transaction:
            return None

        result["date"] = transaction[0]

        amounts = []

        description_parts = []

        for item in transaction[1:]:

            item = item.strip()

            if AMOUNT_PATTERN.match(item):

                amounts.append(item)

            elif item.isdigit():

                result["reference"] = item

            else:

                description_parts.append(
                    item
                )

        result["description"] = (
            " ".join(description_parts)
        )

        if len(amounts) >= 1:

            result["debit"] = (
                amounts[0]
            )

        if len(amounts) >= 2:

            result["balance"] = (
                amounts[-1]
            )

        return result