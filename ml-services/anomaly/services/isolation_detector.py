# services/isolation_detector.py

from sklearn.ensemble import (
    IsolationForest
)

import numpy as np


class IsolationDetector:

    def detect(
        self,
        feature_df
    ):

        if len(feature_df) < 5:

            return []

        model = IsolationForest(

            n_estimators=200,

            contamination=0.05,

            random_state=42
        )

        X = feature_df.drop(
            columns=["account"]
        )

        amount_95 = (
            feature_df[
                "max_txn_amount"
            ]
            .quantile(0.95)
        )

        txn_count_95 = (
            feature_df[
                "txn_count"
            ]
            .quantile(0.95)
        )

        counterparty_95 = (
            feature_df[
                "unique_counterparties"
            ]
            .quantile(0.95)
        )

        model.fit(X)

        scores = (
            -model.decision_function(X)
        )

        scores = (
            scores - scores.min()
        ) / (
            scores.max()
            - scores.min()
            + 1e-9
        )

        score_95 = np.percentile(
            scores,
            95
        )

        score_90 = np.percentile(
            scores,
            90
        )

        results = []

        print("\n========== FEATURE STATS ==========")

        print(
            feature_df[
                [
                    "max_txn_amount",
                    "txn_count",
                    "unique_counterparties"
                ]
            ].describe()
        )

        print(
            "\namount_95:",
            amount_95
        )

        print(
            "txn_count_95:",
            txn_count_95
        )

        print(
            "counterparty_95:",
            counterparty_95
        )
        
        for idx, row in (
            feature_df.iterrows()
        ):

            patterns = []

            # Isolation Forest ranking

            if float(scores[idx]) >= score_95:

                patterns.append(
                    "high_statistical_anomaly"
                )

            elif float(scores[idx]) >= score_90:

                patterns.append(
                    "moderate_statistical_anomaly"
                )


            # Feature explanations

            if (
                row["max_txn_amount"]
                >= amount_95
            ):

                patterns.append(
                    "large_transaction_behavior"
                )

            if (
                row["txn_count"]
                >= txn_count_95
            ):

                patterns.append(
                    "high_transaction_frequency"
                )

            if (
                row["unique_counterparties"]
                >= counterparty_95
            ):

                patterns.append(
                    "high_counterparty_activity"
                )

            if patterns:

                print(
                    f"{row['account']} -> {patterns}"
                )

            results.append({

                "account":
                    row["account"],

                "stat_score":
                    float(scores[idx]),

                "patterns":
                    patterns
            })
        return results