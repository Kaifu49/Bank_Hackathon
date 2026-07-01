from services.postgres_loader import PostgresLoader
from services.burst_detector import BurstDetector
from services.velocity_detector import VelocityDetector
from services.structuring_detector import StructuringDetector


class TemporalService:

    def __init__(self):
        self.loader = PostgresLoader()
        self.detector = BurstDetector()
        self.velocity = VelocityDetector()
        self.structuring = StructuringDetector()

    # -- public API -------------------------------------------------------

    def all(self):
        """Score every account across the whole dataset (GET /temporal)."""
        txns = self.loader.load_all_transactions().to_dict("records")
        return self._score(txns)

    def latest(self):
        txns = self.loader.load_latest_statement_transactions().to_dict("records")
        return self._score(txns)

    def statement(self, statement_id):
        txns = self.loader.load_statement_transactions(statement_id).to_dict("records")
        return self._score(txns)

    def account(self, account):
        for result in self.all():
            if result["account"] == account:
                return result
        return {"account": account, "temporal_score": 0, "patterns": []}

    # -- shared scoring ---------------------------------------------------

    def _score(self, transactions):
        burst = self.detector.detect(transactions)
        velocity = self.velocity.detect(transactions)
        structuring = self.structuring.detect(transactions)

        fused = {}
        for item in burst:
            a = item["account"]
            fused[a] = {"account": a,
                        "temporal_score": item["temporal_score"],
                        "patterns": list(item["patterns"])}
        for item in velocity:
            a = item["account"]
            fused.setdefault(a, {"account": a, "temporal_score": 0, "patterns": []})
            fused[a]["temporal_score"] += item["velocity_score"]
            fused[a]["patterns"].extend(item["patterns"])
        for item in structuring:
            a = item["account"]
            fused.setdefault(a, {"account": a, "temporal_score": 0, "patterns": []})
            fused[a]["temporal_score"] += item["structuring_score"]
            fused[a]["patterns"].extend(item["patterns"])

        for a in fused:
            fused[a]["temporal_score"] = round(min(fused[a]["temporal_score"], 1.0), 4)
            fused[a]["patterns"] = sorted(set(fused[a]["patterns"]))

        return list(fused.values())
