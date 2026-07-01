from services.feature_builder import (
    FeatureBuilder
)

from services.isolation_detector import (
    IsolationDetector
)

from services.postgres_loader import (
    PostgresLoader
)


class AnomalyService:

    def __init__(self):

        self.builder = (
            FeatureBuilder()
        )

        self.detector = (
            IsolationDetector()
        )

        self.loader = (
            PostgresLoader()
        )

    def process(self):
        """Score ALL accounts across the whole dataset (used by GET /anomaly)."""
        transactions = (
            self.loader
            .load_all_transactions()
            .to_dict("records")
        )
        features = self.builder.build(transactions)
        return self.detector.detect(features)

    def latest(self):

        transactions = (
            self.loader
            .load_latest_statement_transactions()
            .to_dict("records")
        )

        features = (
            self.builder.build(
                transactions
            )
        )

        return (
            self.detector.detect(
                features
            )
        )

    def statement(
        self,
        statement_id
    ):

        transactions = (
            self.loader
            .load_statement_transactions(
                statement_id
            )
            .to_dict("records")
        )

        features = (
            self.builder.build(
                transactions
            )
        )

        return (
            self.detector.detect(
                features
            )
        )

    def account(
    self,
    account
):

        results = self.latest()

        for result in results:

            if (
                result["account"]
                == account
            ):
                return result

        return {
            "account": account,
            "stat_score": 0,
            "patterns": []
        }