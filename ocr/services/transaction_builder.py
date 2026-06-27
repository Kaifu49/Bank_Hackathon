import re


AMOUNT_PATTERN = re.compile(
    r"^\d[\d,]*\.\d{2}$"
)


class TransactionBuilder:

    def build(
        self,
        transaction_lines
    ):

        if len(transaction_lines) < 3:
            return None

        date = transaction_lines[0]

        amounts = []

        narration_parts = []

        reference = None

        for item in transaction_lines[1:]:

            if AMOUNT_PATTERN.match(item):

                amounts.append(item)

            elif item.isdigit():

                reference = item

            else:

                narration_parts.append(
                    item
                )

        narration = " ".join(
            narration_parts
        )

        transaction = {
            "Txn Date": date,
            "Description": narration,
            "Ref No": reference,
        }

        if len(amounts) >= 1:
            transaction["Amount"] = amounts[0]

        if len(amounts) >= 2:
            transaction["Balance"] = amounts[-1]

        return transaction