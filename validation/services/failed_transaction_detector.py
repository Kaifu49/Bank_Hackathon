class FailedTransactionDetector:
    """
    Detect failed/reversed transactions (Core Requirement 2).

    The graded definition is "amount debited and then credited back". So the
    primary signal is a REVERSAL PAIR: a debit of amount A followed (within a
    short window) by a credit of the same amount A. Both legs are marked failed.

    A secondary signal is narration keywords (REVERSAL / REFUND / FAILED), which
    catches reversals whose counter-leg isn't in the same statement window.
    """

    REVERSAL_WORDS = ["REVERSAL", "REVERSED", "REFUND", "FAILED",
                      "RETURNED", "CHARGEBACK"]

    def __init__(self, window: int = 10, amount_tolerance: float = 0.01):
        self.window = window
        self.amount_tolerance = amount_tolerance

    def detect(self, transactions):
        self._detect_reversal_pairs(transactions)
        self._detect_keywords(transactions)
        return transactions

    def _detect_reversal_pairs(self, transactions):
        n = len(transactions)
        paired = set()
        for i in range(n):
            d = transactions[i]
            if i in paired:
                continue
            if d.debit_credit != "DEBIT" or not d.amount:
                continue
            # look ahead for a matching credit-back
            for j in range(i + 1, min(i + 1 + self.window, n)):
                if j in paired:
                    continue
                c = transactions[j]
                if c.debit_credit != "CREDIT" or not c.amount:
                    continue
                if abs(c.amount - d.amount) <= self.amount_tolerance:
                    d.is_failed = True
                    c.is_failed = True
                    self._note(d, "reversed_debit")
                    self._note(c, "reversal_credit")
                    paired.add(i)
                    paired.add(j)
                    break

    def _detect_keywords(self, transactions):
        for txn in transactions:
            text = (txn.narration or "").upper()
            if any(w in text for w in self.REVERSAL_WORDS):
                txn.is_failed = True
                self._note(txn, "reversal_keyword")

    @staticmethod
    def _note(txn, note):
        if note not in txn.validation_notes:
            txn.validation_notes.append(note)
