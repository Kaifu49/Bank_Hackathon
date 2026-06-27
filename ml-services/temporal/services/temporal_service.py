from services.postgres_loader import (
    PostgresLoader
)

from services.burst_detector import (
    BurstDetector
)

from services.velocity_detector import (
    VelocityDetector)

from services.structuring_detector import(
    StructuringDetector
)

class TemporalService:

    def __init__(self):

        self.loader = (
            PostgresLoader()
        )

        self.detector = (
            BurstDetector()
        )

        self.velocity = (
            VelocityDetector()
        )

        self.structuring = (
            StructuringDetector()   
        )

    def latest(self):

        transactions = (
            self.loader
            .load_latest_statement_transactions()
            .to_dict("records")
        )

        burst_results = (
            self.detector.detect(
                transactions
            )
        )

        velocity_results = (
            self.velocity.detect(
                transactions
            )
        )

        structuring_results = (
            self.structuring.detect(
                transactions
            )
        )

        fused = {}

        # Burst
        for item in burst_results:

            account = item["account"]

            fused[account] = {

                "account": account,

                "temporal_score":
                    item["temporal_score"],

                "patterns":
                    item["patterns"].copy()
            }

        # Velocity
        for item in velocity_results:

            account = item["account"]

            if account not in fused:

                fused[account] = {

                    "account": account,

                    "temporal_score": 0,

                    "patterns": []
                }

            fused[account]["temporal_score"] += (
                item["velocity_score"]
            )

            fused[account]["patterns"].extend(
                item["patterns"]
            )

        # Structuring
        for item in structuring_results:

            account = item["account"]

            if account not in fused:

                fused[account] = {

                    "account": account,

                    "temporal_score": 0,

                    "patterns": []
                }

            fused[account]["temporal_score"] += (
                item["structuring_score"]
            )

            fused[account]["patterns"].extend(
                item["patterns"]
            )

        # Normalize score
        for account in fused:

            fused[account]["temporal_score"] = min(
                fused[account]["temporal_score"],
                1.0
            )

            fused[account]["patterns"] = list(
                set(
                    fused[account]["patterns"]
                )
            )

        return list(
            fused.values()
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

    # Same logic as latest()

    def account(
        self,
        account
    ):

        results = self.latest()

        for result in results:

            if result["account"] == account:

                return result

        return {
            "account": account,
            "temporal_score": 0,
            "patterns": []
        }