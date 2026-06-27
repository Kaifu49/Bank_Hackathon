import pandas as pd
import numpy as np


class BurstDetector:

    def detect(
        self,
        transactions
    ):

        df = pd.DataFrame(
            transactions
        )

        if df.empty:

            return []

        counts = (

            df.groupby(
                "sender_account"
            )

            .size()

            .reset_index(
                name="txn_count"
            )
        )

        mean_count = (
            counts[
                "txn_count"
            ].mean()
        )

        std_count = (
            counts[
                "txn_count"
            ].std()
        )

        if std_count == 0:

            std_count = 1

        results = []

        for _, row in (
            counts.iterrows()
        ):

            z_score = (

                row["txn_count"]
                - mean_count

            ) / std_count

            temporal_score = min(
                max(
                    z_score / 3,
                    0
                ),
                1
            )

            patterns = []

            if z_score > 2:

                patterns.append(
                    "burst_activity"
                )

            results.append({

                "account":
                    row[
                        "sender_account"
                    ],

                "temporal_score":
                    float(
                        temporal_score
                    ),

                "patterns":
                    patterns
            })

        return results