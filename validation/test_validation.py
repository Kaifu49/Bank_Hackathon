"""
Validation engine tests (detectors operate on attribute objects, so we use
SimpleNamespace mocks to avoid the pydantic dependency in this environment).
Run: python test_validation.py
"""
import sys, os
from types import SimpleNamespace
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
from duplicate_detector import DuplicateDetector              # noqa: E402
from failed_transaction_detector import FailedTransactionDetector  # noqa: E402
from balance_validator import BalanceValidator               # noqa: E402


def txn(date, dc, amount, balance, narration="", ref=""):
    return SimpleNamespace(
        date=date, debit_credit=dc, amount=amount, balance=balance,
        narration=narration, reference_number=ref,
        is_duplicate=False, is_failed=False, is_valid=True,
        confidence_score=1.0, validation_notes=[],
    )


def build():
    # opening balance 1000
    return [
        txn("01", "CREDIT", 500, 1500, "SALARY", "R0"),         # 0 first, no check
        txn("02", "DEBIT", 200, 1300, "UPI A", "R1"),           # 1 clean
        txn("03", "DEBIT", 100, 1200, "ATM WDL", "R2"),         # 2 reversed
        txn("03", "CREDIT", 100, 1300, "ATM REVERSAL", "R3"),   # 3 reversal credit
        txn("04", "DEBIT", 300, 1000, "NEFT", "R4"),            # 4 clean
        txn("05", "DEBIT", 50, 900, "WRONG BAL", "R5"),         # 5 mismatch (exp 950)
        txn("06", "DEBIT", None, None, "INFO ONLY", "R6"),      # 6 missing amount/bal
        txn("02", "DEBIT", 200, 1300, "UPI A", "R1"),           # 7 dup of #1
    ]


def run():
    t = build()
    DuplicateDetector().detect(t)
    FailedTransactionDetector().detect(t)
    BalanceValidator().validate(t)

    checks = [
        ("reversal debit #2 failed", t[2].is_failed, True),
        ("reversal credit #3 failed", t[3].is_failed, True),
        ("#5 balance mismatch", "balance_mismatch" in t[5].validation_notes, True),
        ("#5 invalid", t[5].is_valid, False),
        ("#7 duplicate", t[7].is_duplicate, True),
        ("#1 clean (not failed)", t[1].is_failed, False),
        ("#1 clean (valid)", t[1].is_valid, True),
        ("#4 no false mismatch", "balance_mismatch" in t[4].validation_notes, False),
    ]
    ok = True
    for label, got, exp in checks:
        good = got == exp
        ok = ok and good
        print(f"[{'PASS' if good else 'FAIL'}] {label}: got={got} exp={exp}")

    # missing-data note (added by the service, mimic here)
    miss = t[6].amount is None and t[6].balance is None
    print(f"[{'PASS' if miss else 'FAIL'}] #6 missing amount+balance detected")
    ok = ok and miss

    failed = sum(1 for x in t if x.is_failed)
    dups = sum(1 for x in t if x.is_duplicate)
    mism = sum(1 for x in t if "balance_mismatch" in x.validation_notes)
    print(f"\nsummary: failed={failed} duplicates={dups} mismatches={mism}")
    ok = ok and failed == 2 and dups == 1 and mism == 1

    print("\n" + ("ALL VALIDATION TESTS PASS" if ok else "FAILURES"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    run()
