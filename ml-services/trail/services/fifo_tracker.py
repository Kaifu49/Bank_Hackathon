class FIFOTracker:

    def trace(
        self,
        transactions
    ):

        trails = []

        credits = []

        for txn in transactions:

            if (
                txn["type"]
                .upper()
                ==
                "CREDIT"
            ):

                credits.append(
                    {
                        "credit_amount":
                            txn["amount"],

                        "remaining":
                            txn["amount"],

                        "consumed_by":
                            []
                    }
                )

            else:

                debit_amount = (
                    txn["amount"]
                )

                while (
                    debit_amount > 0
                    and len(credits) > 0
                ):

                    credit =credits[0]

                    consume =min(
                            debit_amount,
                            credit[
                                "remaining"
                            ]
                        )

                    credit[
                        "consumed_by"
                    ].append(
                        {
                            "debit_amount":
                                consume
                        }
                    )

                    credit[
                        "remaining"
                    ] -= consume

                    debit_amount -= consume

                    if (
                        credit[
                            "remaining"
                        ]
                        <= 0
                    ):

                        trails.append(
                            credit
                        )

                        credits.pop(0)

        trails.extend(
            credits
        )

        return trails