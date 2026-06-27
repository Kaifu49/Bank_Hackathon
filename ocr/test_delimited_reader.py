"""
Test delimited_reader + TabularReader on a ragged CSV with a comma-laden
metadata preamble (the case that crashed pandas: "Expected 4 fields, saw 9").
Run: python test_delimited_reader.py
"""
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
import delimited_reader  # noqa: E402
from tabular_reader import TabularReader  # noqa: E402

CSV = """Statement of Account
COLUMN HEADERS: CLG , Cheque Clearing Transaction
COLUMN HEADERS: EDC , Credit transaction through, card
TRAN_DATE,CHQNO,PARTICULARS,DR,CR,BAL,SOL
01-04-2025,,OPENING BALANCE,,,10000.00,292
02-04-2025,,UPI/rahul@ybl/PAYTM,500.00,,9500.00,292
03-04-2025,,NEFT SALARY,,25000.00,34500.00,292
"""


def run():
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     encoding="utf-8") as f:
        f.write(CSV)
        path = f.name
    try:
        grid = delimited_reader.read_grid(path)
        print(f"grid rows={len(grid)}, width={max(len(r) for r in grid)}")
        rows, meta = TabularReader().read_grid(grid)
        print(f"mode={meta['mode']} rows={len(rows)}")
        assert meta["mode"] == "header_detected", meta
        assert len(rows) == 3, len(rows)
        assert rows[1]["PARTICULARS"] == "UPI/rahul@ybl/PAYTM", rows[1]
        assert rows[1]["DR"] == "500.00", rows[1]
        assert rows[2]["CR"] == "25000.00", rows[2]
        print("sample row:", rows[1])
        print("\nALL DELIMITED READER TESTS PASS")
    finally:
        os.unlink(path)


if __name__ == "__main__":
    run()
