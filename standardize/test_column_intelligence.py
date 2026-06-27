"""
Validation harness for column_intelligence against REAL header families
observed in docs/docs/Consolidated_Bank_Data.xlsx.

Run: python test_column_intelligence.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
from column_intelligence import resolve_columns  # noqa: E402

# (label, headers, expected {canonical_field: source_header})
CASES = [
    ("YES BANK PDF",
     ["TXN DATE", "VALUE DATE", "DESCRIPTION", "REFERENCE", "DEBITS", "CREDITS", "BALANCE"],
     {"date": "TXN DATE", "value_date": "VALUE DATE", "narration": "DESCRIPTION",
      "ref_no": "REFERENCE", "debit": "DEBITS", "credit": "CREDITS", "balance": "BALANCE"}),

    ("Compact split (Tran_ID...)",
     ["Tran_ID", "Tran_Date", "Dr_Amt", "Cr_Amt", "Balance", "Narration"],
     {"ref_no": "Tran_ID", "date": "Tran_Date", "debit": "Dr_Amt",
      "credit": "Cr_Amt", "balance": "Balance", "narration": "Narration"}),

    ("IDBI (Debit Amt./Credit Amt.)",
     ["Date", "Tran Ref Num", "Particulars", "Debit Amt.", "Credit Amt.", "Balance Amt.", "Contra"],
     {"date": "Date", "ref_no": "Tran Ref Num", "narration": "Particulars",
      "debit": "Debit Amt.", "credit": "Credit Amt.", "balance": "Balance Amt."}),

    ("Withdrawal/Deposit (SOA)",
     ["DATE", "TRANSACTION DETAILS", "CHQ.NO.", "VALUE DATE", "WITHDRAWAL AMT", "DEPOSIT AMT", "BALANCE AMT"],
     {"date": "DATE", "narration": "TRANSACTION DETAILS", "ref_no": "CHQ.NO.",
      "value_date": "VALUE DATE", "debit": "WITHDRAWAL AMT", "credit": "DEPOSIT AMT",
      "balance": "BALANCE AMT"}),

    ("CSV comma (DR/CR/BAL)",
     ["TRAN_DATE", "CHQNO", "PARTICULARS", "DR", "CR", "BAL", "SOL"],
     {"date": "TRAN_DATE", "ref_no": "CHQNO", "narration": "PARTICULARS",
      "debit": "DR", "credit": "CR", "balance": "BAL"}),

    ("CSV tab (TRAN-DATE...)",
     ["TRAN-DATE", "TRAN_PARTICULAR", "CHQ-NUM", "WITHDRAWAL", "DEPOSIT", "BALANCE"],
     {"date": "TRAN-DATE", "narration": "TRAN_PARTICULAR", "ref_no": "CHQ-NUM",
      "debit": "WITHDRAWAL", "credit": "DEPOSIT", "balance": "BALANCE"}),

    ("Pipe XLSX (full)",
     ["ACCOUNT", "ACCT NAME", "TRAN ID", "TRAN DATE", "VALUE DATE", "TRAN TYPE",
      "TRAN SUB TYPE", "DEBIT", "CREDIT", "BALANCE"],
     {"account": "ACCOUNT", "ref_no": "TRAN ID", "date": "TRAN DATE",
      "value_date": "VALUE DATE", "txn_type": "TRAN TYPE", "debit": "DEBIT",
      "credit": "CREDIT", "balance": "BALANCE"}),

    ("Withdrawals/Deposits (Tran. Type)",
     ["Tran. Date", "Tran. Type", "Cheque No.", "Transaction Particulars",
      "Tran. Remarks", "Withdrawals", "Deposits", "Balance(Rs.)"],
     {"date": "Tran. Date", "txn_type": "Tran. Type", "ref_no": "Cheque No.",
      "narration": "Transaction Particulars", "debit": "Withdrawals",
      "credit": "Deposits", "balance": "Balance(Rs.)"}),

    ("Bank of Maharashtra style",
     ["TRAN DATE", "TRAN PARTICULAR", "INSTRUMENT NO", "DEBIT AMOUNT", "CREDIT", "BALANCE"],
     {"date": "TRAN DATE", "narration": "TRAN PARTICULAR", "ref_no": "INSTRUMENT NO",
      "debit": "DEBIT AMOUNT", "credit": "CREDIT", "balance": "BALANCE"}),

    ("Signed single-amount layout",
     ["Txn Date", "Description", "Amount", "Balance"],
     {"date": "Txn Date", "narration": "Description", "amount": "Amount",
      "balance": "Balance"}),

    # Wide bank export: holder ACCOUNT NO. must NOT become sender_account.
    ("Wide CBS export (26 cols)",
     ["ACCOUNT NO.", "TRAN DATE", "VALUE DATE", "TRAN PARTICULAR",
      "INSTRUMENT NO", "DEBIT AMOUNT", "CREDIT AMOUNT", "BALANCE AMOUNT",
      "BALANCE INDICATOR", "ACCOUNT NAME", "SOL ID", "TRAN ID", "TRAN AMT",
      "TRAN TYPE", "TRAN SUB TYPE", "PART TRAN TYPE", "TRAN RMKS",
      "BENEF/REMIT ACCT NO", "BENEF/REMIT ACCT NAME"],
     {"account": "ACCOUNT NO.", "date": "TRAN DATE", "value_date": "VALUE DATE",
      "narration": "TRAN PARTICULAR", "ref_no": "INSTRUMENT NO",
      "debit": "DEBIT AMOUNT", "credit": "CREDIT AMOUNT",
      "balance": "BALANCE AMOUNT"}),
]

# Headers that must NOT map to per-transaction sender/receiver fields.
MUST_NOT_MAP = [
    ("Wide CBS export (26 cols)",
     ["ACCOUNT NO.", "ACCOUNT NAME", "BENEF/REMIT ACCT NAME"],
     ["sender_account", "receiver_account"]),
]


def run():
    total = 0
    passed = 0
    failures = []
    for label, headers, expected in CASES:
        res = resolve_columns(headers)
        # invert mapping: canonical -> source
        got = {}
        for src, canon in res.mapping.items():
            got[canon] = src
        ok = True
        detail = []
        for canon, src in expected.items():
            total += 1
            if got.get(canon) == src:
                passed += 1
            else:
                ok = False
                detail.append(f"    {canon}: expected '{src}', got '{got.get(canon)}'")
        status = "PASS" if ok else "FAIL"
        amode = res.amount_mode
        print(f"[{status}] {label}  (amount_mode={amode}, conf={res.overall_confidence()})")
        if not ok:
            failures.append((label, detail))
        if res.unmapped:
            print(f"    unmapped: {res.unmapped}")
    # Negative checks: holder/account-name headers must not become counterparties
    for label, headers, forbidden in MUST_NOT_MAP:
        res = resolve_columns(headers)
        mapped_fields = set(res.mapping.values())
        bad = [f for f in forbidden if f in mapped_fields]
        if bad:
            print(f"[FAIL] {label}: unexpectedly mapped {bad} from {headers}")
            failures.append((label, [f"    mapped forbidden: {bad}"]))
        else:
            print(f"[PASS] {label}: no forbidden counterparty mapping")

    print()
    print(f"FIELD-LEVEL: {passed}/{total} correct")
    if failures:
        print("\nFAILURES:")
        for label, detail in failures:
            print(f"  {label}:")
            print("\n".join(detail))
        sys.exit(1)
    else:
        print("ALL CASES PASS")


if __name__ == "__main__":
    run()
