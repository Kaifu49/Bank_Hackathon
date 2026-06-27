class BalanceValidator:
    """
    Verify running-balance consistency (Core Requirement 2).

    Correct invariant for a chronologically ordered ledger:

        balance[i] == balance[i-1] + credit[i] - debit[i]

    i.e. apply THIS transaction's amount/direction to the PREVIOUS balance to
    arrive at THIS balance. (The previous implementation applied the current
    txn's amount to the current balance to predict the next — the wrong
    relationship.)

    Rows adjacent to a missing balance are skipped (we can't bridge the gap),
    and failed/reversed legs are tolerated since they still move the balance.
    """

    def __init__(self, tolerance: float = 1.0):
        self.tolerance = tolerance

    def validate(self, transactions):
        prev_balance = None
        for txn in transactions:
            cur_balance = txn.balance

            can_check = (
                prev_balance is not None
                and cur_balance is not None
                and txn.amount is not None
                and txn.debit_credit in ("DEBIT", "CREDIT")
            )
            if can_check:
                signed = txn.amount if txn.debit_credit == "CREDIT" else -txn.amount
                expected = prev_balance + signed
                if abs(expected - cur_balance) > self.tolerance:
                    txn.is_valid = False
                    if "balance_mismatch" not in txn.validation_notes:
                        txn.validation_notes.append("balance_mismatch")

            # advance the reference balance (reset across gaps)
            prev_balance = cur_balance

        return transactions
