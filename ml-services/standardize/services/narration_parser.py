class NarrationParser:

    def parse(
        self,
        narration
    ):

        text = (
            narration.upper()
            if narration
            else ""
        )

        txn_type = (
            "UNCLASSIFIED"
        )

        if "UPI" in text:

            txn_type = "UPI"

        elif "IMPS" in text:

            txn_type = "IMPS"

        elif "NEFT" in text:

            txn_type = "NEFT"

        elif "RTGS" in text:

            txn_type = "RTGS"

        elif "ATM" in text:

            txn_type = "ATM"

        elif "CHEQUE" in text:

            txn_type = "CHEQUE"

        elif "CASH" in text:

            txn_type = "CASH"

        elif "SALARY" in text:

            txn_type = "SALARY"

        elif "EMI" in text:

            txn_type = "EMI"

        return {

            "txn_type":
                txn_type,

            "platform":
                None,

            "upi_id":
                None
        }