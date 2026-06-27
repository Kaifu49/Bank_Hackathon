class BalanceValidator:

    def validate(
        self,
        transactions
    ):

        if len(transactions) < 2:
            return transactions

        for i in range(
            len(transactions) - 1
        ):

            current = transactions[i]

            nxt = transactions[i + 1]

            if (
                current.balance is None
                or nxt.balance is None
            ):
                continue

            expected = current.balance

            if (
                current.debit_credit
                == "DEBIT"
            ):

                expected -= (
                    current.amount or 0
                )

            elif (
                current.debit_credit
                == "CREDIT"
            ):

                expected += (
                    current.amount or 0
                )

            if abs(
                expected - nxt.balance
            ) > 1:

                nxt.is_valid = False

                nxt.validation_notes.append(
                    "balance_mismatch"
                )

        return transactions