"""
Validate TextStatementReconstructor against the REAL IDFC First Bank text PDF
extract (the one that caused the 422). Run: python test_text_reconstructor.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
from text_statement_reconstructor import TextStatementReconstructor  # noqa: E402

PAGE1 = """STATEMENT OF ACCOUNT
CUSTOMER ID : 3680115808
ACCOUNT NO : 87889641689
STATEMENT FOR 17-Apr-2025 TO 01-Dec-2025
Mr. Harish Kumar ACCOUNT :LUCKNOW BRANCH
IFSC Code :IDFB0021251
Opening Balance Total Debits Total Credits Closing Balance
0.00 1,083,492.00 1,083,562.00 70.00Cr
Trans Date and Value Date Ref/Cheque
Transaction Details Debit Credit Balance
Time No
Opening Balance 0.00
OLSAIP/17440570250417142558800/5107
17/04/25 14:26 17/04/25 92244994/UPI 25,100.00 25,100.00Cr
IMPS-
OPM/510714100618/SHAFIQ/YESB000041
17/04/25 14:40 17/04/25 5,000.00 20,100.00Cr
9/8578/
UPI/MOB/510791392117/Pay request
17/04/25 14:45 17/04/25 5,000.00 15,100.00Cr
IMPS-
OPM/510715173633/SHAFIQ/YESB000041
17/04/25 15:17 17/04/25 15,000.00 100.00Cr
9/8578/
UPI/MOB/511998194205/Pay request
29/04/25 12:37 29/04/25 50.00 50.00Cr
UPI/MOB/511998277587/Pay request
29/04/25 15:07 29/04/25 10.00 40.00Cr
IMPS/511916044301/RESEARCHINSTITU/Y
ESB0000001/0102/CREDIT202504291610
29/04/25 16:10 29/04/25 197,598.00 197,638.00Cr
095049HarishKumar
ATM/CASH
29/04/25 16:16 29/04/25 WITHDRAWAL/3645/SARSAWAN 20,000.00 177,638.00Cr
BRANCH ATM LUCKNOW UP IN/SELF
REGISTERED OFFICE : IDFC FIRST BANK LIMITED, KRM Tower, Page 1 Of6
Chennai – 600031, Tamil Nadu, INDIA"""

# expected (date, dr_or_cr, amount, balance) in order
EXPECTED = [
    ("17/04/25", "credit", 25100.00, 25100.00),
    ("17/04/25", "debit",   5000.00, 20100.00),
    ("17/04/25", "debit",   5000.00, 15100.00),
    ("17/04/25", "debit",  15000.00,   100.00),
    ("29/04/25", "debit",     50.00,    50.00),
    ("29/04/25", "debit",     10.00,    40.00),
    ("29/04/25", "credit", 197598.00, 197638.00),
    ("29/04/25", "debit",  20000.00, 177638.00),
]


def run():
    rows = TextStatementReconstructor().reconstruct([PAGE1])
    print(f"Reconstructed {len(rows)} transactions (expected {len(EXPECTED)})\n")
    ok = True
    for i, exp in enumerate(EXPECTED):
        if i >= len(rows):
            print(f"[FAIL] row {i}: missing")
            ok = False
            continue
        r = rows[i]
        edate, ekind, eamt, ebal = exp
        amt = r["debit"] if r["debit"] is not None else r["credit"]
        kind = "debit" if r["debit"] is not None else ("credit" if r["credit"] is not None else "none")
        row_ok = (r["date"] == edate and kind == ekind
                  and abs((amt or 0) - eamt) < 0.01
                  and abs((r["balance"] or 0) - ebal) < 0.01)
        ok = ok and row_ok
        flag = "PASS" if row_ok else "FAIL"
        print(f"[{flag}] {r['date']} {kind:6} amt={amt} bal={r['balance']}  "
              f"narr={ (r['narration'] or '')[:42] }")
        if not row_ok:
            print(f"        expected {edate} {ekind} {eamt} bal={ebal}")
    print()
    if ok and len(rows) == len(EXPECTED):
        print("ALL TRANSACTIONS CORRECT")
    else:
        print("MISMATCH")
        sys.exit(1)


if __name__ == "__main__":
    run()
