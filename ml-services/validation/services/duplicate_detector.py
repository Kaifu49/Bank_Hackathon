class DuplicateDetector:

    def detect(
        self,
        transactions
    ):

        seen = set()

        for txn in transactions:

            key = (
                txn.date,
                txn.amount,
                txn.reference_number,
                txn.narration
            )

            if key in seen:

                txn.is_duplicate = True

                txn.validation_notes.append(
                    "duplicate_transaction"
                )

            else:

                seen.add(key)

        return transactions