"""
ValidationService — Core Requirement 2 (Data Cleaning & Validation).

Pipeline per upload:
  1. Missing/incorrect-data checks (date / amount / balance present & sane)
  2. Duplicate detection (exact duplicate ledger lines)
  3. Failed/reversed transaction detection (debit -> credit-back pairs + keywords)
  4. Running-balance consistency

Each transaction is annotated with is_duplicate / is_failed / is_valid /
confidence_score / validation_notes. The service also returns a summary used by
the backend's /statements/{id}/validation-report endpoint.
"""

from models.validation_models import ValidatedTransaction
from services.duplicate_detector import DuplicateDetector
from services.failed_transaction_detector import FailedTransactionDetector
from services.balance_validator import BalanceValidator


# confidence penalties per issue (subtracted from 1.0, clamped to [0,1])
_PENALTY = {
    "missing_amount": 0.4,
    "missing_date": 0.2,
    "missing_balance": 0.15,
    "balance_mismatch": 0.4,
    "duplicate_transaction": 0.2,
}


class ValidationService:

    def __init__(self):
        self.duplicate_detector = DuplicateDetector()
        self.failed_detector = FailedTransactionDetector()
        self.balance_validator = BalanceValidator()

    def process(self, transactions):
        validated, _summary = self.process_with_summary(transactions)
        return validated

    def process_with_summary(self, transactions):
        validated = [
            ValidatedTransaction(**txn) if isinstance(txn, dict) else txn
            for txn in (transactions or [])
        ]

        self._check_missing_data(validated)
        self.duplicate_detector.detect(validated)
        self.failed_detector.detect(validated)
        self.balance_validator.validate(validated)
        self._score_confidence(validated)

        return validated, self._summarize(validated)

    # -- internals --------------------------------------------------------

    def _check_missing_data(self, transactions):
        for txn in transactions:
            if not txn.date:
                self._note(txn, "missing_date")
            if txn.amount is None:
                self._note(txn, "missing_amount")
            if txn.balance is None:
                self._note(txn, "missing_balance")

    def _score_confidence(self, transactions):
        for txn in transactions:
            score = 1.0
            for note in set(txn.validation_notes):
                score -= _PENALTY.get(note, 0.0)
            txn.confidence_score = round(max(0.0, min(1.0, score)), 3)
            # A row with no usable amount is not a usable transaction.
            if "missing_amount" in txn.validation_notes:
                txn.is_valid = False

    def _summarize(self, transactions):
        total = len(transactions)
        duplicates = sum(1 for t in transactions if t.is_duplicate)
        failed = sum(1 for t in transactions if t.is_failed)
        mismatch = sum(1 for t in transactions
                       if "balance_mismatch" in t.validation_notes)
        missing = sum(1 for t in transactions if any(
            n.startswith("missing_") for n in t.validation_notes))
        invalid = sum(1 for t in transactions if not t.is_valid)
        return {
            "total": total,
            "valid": total - invalid,
            "invalid": invalid,
            "duplicates": duplicates,
            "failed_or_reversed": failed,
            "balance_mismatches": mismatch,
            "missing_data": missing,
            "average_confidence": round(
                sum(t.confidence_score for t in transactions) / total, 3
            ) if total else 0.0,
        }

    @staticmethod
    def _note(txn, note):
        if note not in txn.validation_notes:
            txn.validation_notes.append(note)
