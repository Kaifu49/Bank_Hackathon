"""
Tests for TabularReader: content inference (headerless) + header detection.
Run: python test_tabular_reader.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
from tabular_reader import TabularReader  # noqa: E402

reader = TabularReader()


def test_headerless_like_sample():
    # Mirrors the user's "Unnamed: N" file: col2=date, col3=desc,
    # col6=ref, col7=particulars, col10=debit, col11=credit, col12=balance.
    # Sequential balances so balance-delta debit/credit works.
    grid = [
        ["37525","06-05-2025 08:54:57","06-05-2025","ATM WITHDRAWAL","","",
         "512608026731","ATM Cash-PBGN3020 BANGALORE","20250506 ","33",
         "200","0","800.41"],
        ["1530","07-05-2025 02:19:04","07-05-2025","Interest Credit","","",
         "","SBINT FOR THE PERIOD","CHBATCH0996 ","996",
         "0","4","804.41"],
        ["1417","08-05-2025 00:10:17","08-05-2025","ATM WITHDRAWAL","","",
         "512608026999","ATM Cash second withdrawal","20250508 ","33",
         "50","0","754.41"],
        ["1506","09-05-2025 23:15:40","09-05-2025","NEFT CREDIT","","",
         "987654321012","NEFT FROM ACME CORP","CHBATCH0997 ","996",
         "0","100","854.41"],
    ]
    rows, meta = reader.read_grid(grid)
    print(f"[headerless] mode={meta['mode']} rows={len(rows)}")
    assert meta["mode"] == "content_inferred", meta
    assert len(rows) == 4, len(rows)
    r0, r1, r2, r3 = rows
    checks = [
        ("date", r0.get("date"), "06-05-2025"),
        ("balance", r0.get("balance"), "800.41"),
        ("debit", r0.get("debit"), "200"),
        ("credit row debit raw 0", r1.get("debit"), "0"),
        ("credit row credit", r1.get("credit"), "4"),
        ("debit row2", r2.get("debit"), "50"),
        ("credit row3", r3.get("credit"), "100"),
    ]
    ok = True
    for label, got, exp in checks:
        good = got == exp
        ok = ok and good
        print(f"   [{'PASS' if good else 'FAIL'}] {label}: got={got!r} exp={exp!r}")
    print(f"   narration r0: {r0.get('narration')!r}")
    print(f"   ref_no r0: {r0.get('ref_no')!r}")
    assert ok
    return True


def test_header_not_row0():
    # Metadata/title rows above the real transaction header.
    grid = [
        ["ACCOUNT STATEMENT", "", "", "", "", ""],
        ["Account No", "123456789", "", "", "", ""],
        ["", "", "", "", "", ""],
        ["Txn Date", "Particulars", "Cheque No", "Withdrawals", "Deposits", "Balance"],
        ["01-04-2025", "OPENING BALANCE", "", "", "", "10,000.00"],
        ["02-04-2025", "UPI PAYTM", "", "500.00", "", "9,500.00"],
        ["03-04-2025", "SALARY", "", "", "25,000.00", "34,500.00"],
    ]
    rows, meta = reader.read_grid(grid)
    print(f"\n[header-not-row0] mode={meta['mode']} rows={len(rows)}")
    assert meta["mode"] == "header_detected", meta
    assert len(rows) == 3, len(rows)
    assert rows[1].get("Withdrawals") == "500.00", rows[1]
    assert rows[2].get("Deposits") == "25,000.00", rows[2]
    print(f"   [PASS] header row correctly located; sample row: {rows[1]}")
    return True


def test_free_text_not_forced():
    # A 1-column free-text grid must NOT be force-parsed as a table.
    grid = [["Dear customer, your statement is ready."],
            ["Thank you for banking with us."]]
    rows, meta = reader.read_grid(grid)
    print(f"\n[free-text] mode={meta['mode']} rows={len(rows)}")
    assert rows == [], rows
    print("   [PASS] free text left for text reconstruction")
    return True


if __name__ == "__main__":
    test_headerless_like_sample()
    test_header_not_row0()
    test_free_text_not_forced()
    print("\nALL TABULAR READER TESTS PASS")
