"""
Unit test for PdfTableExtractor using synthetic pdfplumber-style tables.
Run: python test_pdf_table_extractor.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
from pdf_table_extractor import PdfTableExtractor  # noqa: E402

ex = PdfTableExtractor()

# --- Page 1: a metadata table (must be ignored) + a transaction table -------
META_TABLE = [
    ["Account No", "87889641689"],
    ["IFSC", "IDFB0021251"],
    ["Account Type", "Savings"],
]
TXN_TABLE_P1 = [
    ["Txn Date", "Particulars", "Cheque No", "Withdrawals", "Deposits", "Balance"],
    ["01-04-2025", "OPENING BALANCE", "", "", "", "10,000.00"],
    ["02-04-2025", "UPI/rahul@ybl/PAYTM", "", "500.00", "", "9,500.00"],
    ["03-04-2025", "NEFT SALARY ACME", "", "", "25,000.00", "34,500.00"],
    ["Txn Date", "Particulars", "Cheque No", "Withdrawals", "Deposits", "Balance"],  # repeated header
    ["", "", "", "", "", ""],  # blank
]

# --- Page 2: headerless CONTINUATION of the same table -----------------------
TXN_TABLE_P2 = [
    ["04-04-2025", "ATM CASH WDL", "", "2,000.00", "", "32,500.00"],
    ["05-04-2025", "IMPS FROM JOHN", "", "", "1,000.00", "33,500.00"],
]

# --- Page 2 also has an unrelated footer table (must be ignored) -------------
FOOTER_TABLE = [
    ["Contact Us", "1800-10-888"],
    ["Email", "banker@bank.com"],
]


def run():
    rows = []
    carry = None
    # simulate page-by-page table iteration
    for table in [META_TABLE, TXN_TABLE_P1]:
        got, carry = ex.process_table(table, carry)
        rows.extend(got)
    for table in [TXN_TABLE_P2, FOOTER_TABLE]:
        got, carry = ex.process_table(table, carry)
        rows.extend(got)

    expected = [
        ("01-04-2025", "OPENING BALANCE", "", "", "10,000.00"),
        ("02-04-2025", "UPI/rahul@ybl/PAYTM", "500.00", "", "9,500.00"),
        ("03-04-2025", "NEFT SALARY ACME", "", "25,000.00", "34,500.00"),
        ("04-04-2025", "ATM CASH WDL", "2,000.00", "", "32,500.00"),
        ("05-04-2025", "IMPS FROM JOHN", "", "1,000.00", "33,500.00"),
    ]

    print(f"Extracted {len(rows)} rows (expected {len(expected)})\n")
    ok = len(rows) == len(expected)
    for i, exp in enumerate(expected):
        if i >= len(rows):
            print(f"[FAIL] row {i} missing"); ok = False; continue
        r = rows[i]
        got = (r.get("Txn Date"), r.get("Particulars"),
               r.get("Withdrawals") or "", r.get("Deposits") or "",
               r.get("Balance"))
        row_ok = got == exp
        ok = ok and row_ok
        print(f"[{'PASS' if row_ok else 'FAIL'}] {got}")
        if not row_ok:
            print(f"        expected {exp}")
    print()
    print("ALL TABLE ROWS CORRECT" if ok else "MISMATCH")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    run()
