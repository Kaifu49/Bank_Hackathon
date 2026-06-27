# services/feature_builder.py

import pandas as pd


class FeatureBuilder:

    def build(
        self,
        transactions
    ):

        df = pd.DataFrame(
            transactions
        )

        if df.empty:
            return pd.DataFrame()

        features = []

        for account in (
            df["sender_account"]
            .dropna()
            .unique()
        ):

            account_txns = df[
                df["sender_account"]
                == account
            ]

            amounts = (
                account_txns["amount"]
                .fillna(0)
                .astype(float)
            )

            feature_row = {

                "account":
                    account,

                "mean_txn_amount":
                    amounts.mean(),

                "std_txn_amount":
                    amounts.std(),

                "max_txn_amount":
                    amounts.max(),

                "txn_count":
                    len(account_txns),

                "unique_counterparties":
                    account_txns[
                        "receiver_account"
                    ]
                    .nunique(),

                "large_txn_ratio":
                    (
                        amounts > 50000
                    ).mean()
            }

            features.append(
                feature_row
            )

        return pd.DataFrame(
            features
        )