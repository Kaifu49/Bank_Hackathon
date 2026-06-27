class FailedTransactionDetector:

    REVERSAL_WORDS = [

        "REVERSAL",
        "FAILED",
        "REFUND",
        "REVERSED"

    ]

    def detect(
        self,
        transactions
    ):

        for txn in transactions:

            narration = (
                txn.narration or ""
            ).upper()

            if any(
                word in narration
                for word in self.REVERSAL_WORDS
            ):

                txn.is_failed = True

                txn.validation_notes.append(
                    "failed_transaction"
                )

        return transactions