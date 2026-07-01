import pandas as pd
import numpy as np


class VelocityDetector:

    def detect(
        self,
        transactions
    ):

        df = pd.DataFrame(
            transactions
        )

        if df.empty:

            return []

        df["amount"] = (
            df["amount"]
            .fillna(0)
            .astype(float)
        )

        daily = (

            df.groupby(
                [
                    "sender_account",
                    "date"
                ]
            )["amount"]

            .sum()

            .reset_index()
        )

        account_totals = (

            daily.groupby(
                "sender_account"
            )["amount"]

            .mean()

            .reset_index(
                name="avg_daily_amount"
            )
        )

        mean_daily = (
            account_totals[
                "avg_daily_amount"
            ].mean()
        )

        std_daily = (
            account_totals[
                "avg_daily_amount"
            ].std()
        )

        if std_daily == 0:

            std_daily = 1

        results = []

        for _, row in (
            account_totals.iterrows()
        ):

            z_score = (

                row[
                    "avg_daily_amount"
                ]

                - mean_daily

            ) / std_daily

            score = min(
                max(
                    z_score / 3,
                    0
                ),
                1
            )

            patterns = []

            if z_score > 2:

                patterns.append(
                    "velocity_spike"
                )

            results.append({

                "account":
                    row[
                        "sender_account"
                    ],

                "velocity_score":
                    float(score),

                "patterns":
                    patterns
            })

        return results