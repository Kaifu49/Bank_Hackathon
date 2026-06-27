COLUMN_MAPPINGS = {

    "date": [
        "date",
        "txn date",
        "transaction date",
        "value date"
    ],

    "narration": [
        "narration",
        "description",
        "remarks",
        "particulars",
        "details"
    ],

    "transaction_id": [
        "transaction id",
        "txn id",
        "utr",
        "ref no",
        "reference"
    ],

    "debit": [
        "debit",
        "withdrawal",
        "withdraw"
    ],

    "credit": [
        "credit",
        "deposit"
    ],

    "balance": [
        "balance",
        "closing balance",
        "available balance"
    ],

    # --------------------------------
    # Investigation Dataset Support
    # --------------------------------

    "sender_account": [
        "sender",
        "from_account",
        "source_account"
    ],

    "receiver_account": [
        "receiver",
        "to_account",
        "destination_account"
    ],

    "amount": [
        "amount",
        "transaction_amount"
    ],

    "bank_name": [
        "bank",
        "bank_name"
    ],

    "txn_type": [
        
        "txn_type",
        "transaction_type"
    ]
}
def map_columns(
    headers: list[str]
):

    mapping = {}

    for header in headers:

        normalized = (
            header
            .strip()
            .lower()
        )

        for target, aliases in (
            COLUMN_MAPPINGS.items()
        ):

            if any(
                alias in normalized
                for alias in aliases
            ):

                mapping[header] = target

    return mapping