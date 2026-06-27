from models.validation_models import (
    ValidatedTransaction
)

from services.duplicate_detector import (
    DuplicateDetector
)

from services.failed_transaction_detector import (
    FailedTransactionDetector
)

from services.balance_validator import (
    BalanceValidator
)


class ValidationService:

    def __init__(self):

        self.duplicate_detector = (
            DuplicateDetector()
        )

        self.failed_detector = (
            FailedTransactionDetector()
        )

        self.balance_validator = (
            BalanceValidator()
        )

    def process(
        self,
        transactions
    ):

        validated = []

        for txn in transactions:

            validated.append(
                ValidatedTransaction(
                    **txn
                )
            )

        validated = (
            self.duplicate_detector.detect(
                validated
            )
        )

        validated = (
            self.failed_detector.detect(
                validated
            )
        )

        validated = (
            self.balance_validator.validate(
                validated
            )
        )

        return validated