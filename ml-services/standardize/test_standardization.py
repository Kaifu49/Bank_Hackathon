from services.standardization_service import (
    StandardizationService
)

service = StandardizationService()

sample_rows = [
    {
        "Txn Date": "01/05/2025",
        "Description": "UPI PAYMENT",
        "Debit": 500,
        "Balance": 9500
    }
]

result = service.process(
    sample_rows
)

for row in result:
    print(
        row.model_dump()
    )