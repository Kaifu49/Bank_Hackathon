from models.transaction import StandardizedTransaction
from services.date_normalizer import DateNormalizer
from services.amount_normalizer import AmountNormalizer
from services.narration_parser import NarrationParser


class TransactionEnricher:
    """
    Single unified enrichment path for ALL statement types.

    The previous implementation had a separate "investigation dataset" branch
    that fired whenever a sender/receiver account was present and DISCARDED
    narration, balance and debit/credit. Real bank statements carry all of
    those, so that branch destroyed data. This version always populates every
    field and additionally carries sender/receiver/bank when present.
    """

    def __init__(self):
        self.date_norm = DateNormalizer()
        self.amount_norm = AmountNormalizer()
        self.parser = NarrationParser()

    def enrich(self, txn):
        parsed = self.parser.parse(txn.narration)

        debit = self.amount_norm.normalize(txn.debit)
        credit = self.amount_norm.normalize(txn.credit)

        # Direction & amount from split debit/credit columns first.
        if debit:
            amount, direction = debit, "DEBIT"
        elif credit:
            amount, direction = credit, "CREDIT"
        else:
            # Fall back to an explicit single amount column (signed layouts).
            amount = self.amount_norm.normalize(txn.amount)
            direction = None

        # Prefer narration-derived class (UPI/IMPS/NEFT/...) over a raw code.
        ptype = parsed.get("txn_type")
        txn_type = ptype if ptype and ptype != "UNCLASSIFIED" else txn.txn_type

        return StandardizedTransaction(
            date=self.date_norm.normalize(txn.date),
            amount=amount,
            txn_type=txn_type,
            reference_number=txn.transaction_id,
            narration=txn.narration,
            narration_normalized=txn.narration,
            balance=self.amount_norm.normalize(txn.balance, signed=True),
            debit_credit=direction,
            platform=parsed.get("platform"),
            upi_id=parsed.get("upi_id"),
            sender_account=txn.sender_account,
            receiver_account=txn.receiver_account,
            bank_name=txn.bank_name,
        )
