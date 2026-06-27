from models.transaction import (
    StandardizedTransaction
)

from services.date_normalizer import (
    DateNormalizer
)

from services.amount_normalizer import (
    AmountNormalizer
)

from services.narration_parser import (
    NarrationParser
)


class TransactionEnricher:

    def __init__(self):

        self.date_norm = (
            DateNormalizer()
        )

        self.amount_norm = (
            AmountNormalizer()
        )

        self.parser = (
            NarrationParser()
        )

    def enrich(
        self,
        txn
    ):
        
        # --------------------------------
# Investigation Dataset Path
# --------------------------------

        if (
            txn.sender_account
            or txn.receiver_account
        ):

            return StandardizedTransaction(

                date=
                    self.date_norm.normalize(
                        txn.date
                    ),

                amount=
                    float(txn.amount)
                    if txn.amount is not None
                    else None,

                txn_type=
                    txn.txn_type,

                sender_account=
                    txn.sender_account,

                receiver_account=
                    txn.receiver_account,

                bank_name=
                    txn.bank_name,

                debit_credit=None,

                narration=None,

                narration_normalized=None,

                reference_number=None,

                balance=None,

                platform=None,

                upi_id=None
            )

        parsed = (
            self.parser.parse(
                txn.narration
            )
        )

        debit = (
            self.amount_norm.normalize(
                txn.debit
            )
        )

        credit = (
            self.amount_norm.normalize(
                txn.credit
            )
        )

        amount = (
            debit
            if debit is not None
            else credit
        )

        debit_credit = (
            "DEBIT"
            if debit is not None
            else "CREDIT"
        )

        return StandardizedTransaction(

            date=
                self.date_norm.normalize(
                    txn.date
                ),

            amount=amount,

            txn_type=
                parsed["txn_type"],

            reference_number=
                txn.transaction_id,

            narration=
                txn.narration,

            narration_normalized=
                txn.narration,

            balance=
                self.amount_norm.normalize(
                    txn.balance
                ),

            debit_credit=
                debit_credit,

            platform=
                parsed["platform"],

            upi_id=
                parsed["upi_id"]
        )