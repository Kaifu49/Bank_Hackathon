import pandas as pd


class StructuringDetector:

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

        results = []

        grouped = (
            df.groupby(
                "sender_account"
            )
        )

        for account, group in grouped:

            suspicious = group[

                (group["amount"] >= 45000)

                &

                (group["amount"] <= 50000)

            ]

            count = len(
                suspicious
            )

            score = min(
                count / 10,
                1
            )

            patterns = []

            if count >= 3:

                patterns.append(
                    "structuring_detected"
                )

            results.append({

                "account":
                    account,

                "structuring_score":
                    float(score),

                "patterns":
                    patterns
            })

        return results