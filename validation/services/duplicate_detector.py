class DuplicateDetector:
    """
    Flag exact duplicate transaction rows (Core Requirement 2).

    Conservative composite key: two rows are duplicates only if date, amount,
    direction, reference, narration AND running balance all match. Including the
    balance prevents false positives for genuinely repeated payments (same
    payee/amount/day) — those land on different running balances, so they are
    NOT flagged. Only a truly duplicated ledger line (identical balance too) is.
    """

    def detect(self, transactions):
        seen = set()
        for txn in transactions:
            key = (
                txn.date,
                txn.amount,
                txn.debit_credit,
                (txn.reference_number or "").strip() or None,
                (txn.narration or "").strip() or None,
                txn.balance,
            )
            if key in seen:
                txn.is_duplicate = True
                if "duplicate_transaction" not in txn.validation_notes:
                    txn.validation_notes.append("duplicate_transaction")
            else:
                seen.add(key)
        return transactions
