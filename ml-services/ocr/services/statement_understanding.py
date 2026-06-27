from services.table_detector import (
    TableDetector
)

from services.header_detector import (
    HeaderDetector
)

from services.transaction_reconstructor import (
    TransactionReconstructor
)

from services.transaction_builder import (
    TransactionBuilder
)


class StatementUnderstandingEngine:

    def __init__(self):

        self.table_detector = (
            TableDetector()
        )

        self.header_detector = (
            HeaderDetector()
        )

        self.reconstructor = (
            TransactionReconstructor()
        )

        self.builder = (
            TransactionBuilder()
        )

    def process(
        self,
        rows: list[str]
    ):

        # Find start of transaction table
        table_start = (
            self.table_detector
            .find_table_start(rows)
        )

        if table_start is None:

            print(
                "[DEBUG] No transaction table detected."
            )

            return []

        print(
            f"[DEBUG] Table starts at row {table_start}"
        )

        # Everything after table start
        table_rows = rows[table_start:]

        # Reconstruct transactions from broken OCR lines
        reconstructed_transactions = (
            self.reconstructor
            .reconstruct(table_rows)
        )

        print(
            f"[DEBUG] Reconstructed {len(reconstructed_transactions)} transactions"
        )

        structured_transactions = []

        for transaction in reconstructed_transactions:

            built_transaction = (
                self.builder
                .build(transaction)
            )

            if built_transaction:

                structured_transactions.append(
                    built_transaction
                )

        print(
            f"[DEBUG] Built {len(structured_transactions)} structured transactions"
        )

        return structured_transactions