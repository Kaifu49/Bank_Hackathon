from models.canonical_transaction import (
    CanonicalTransaction
)


def standardize_row(
    row,
    mapping,
):

    data = {}

    for source_col, target_col in (
        mapping.items()
    ):

        data[target_col] = row.get(
            source_col
        )

    return CanonicalTransaction(
        **data
    )