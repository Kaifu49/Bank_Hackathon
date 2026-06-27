"""
ContentColumnProfiler — infer canonical columns from VALUES when a tabular
file (CSV/XLS/XLSX/TXT) has no usable header row (pandas yields ``Unnamed: N``).

It profiles each column by content and assigns canonical fields:
``date, narration, ref_no, debit, credit, balance``. Debit vs credit is
disambiguated using the running-balance delta (the same bank-agnostic trick used
for text PDFs): the amount column that is non-zero when the balance *drops* is
the debit column; when it *rises*, the credit column.

Emits rows keyed by canonical names, so the downstream Column Intelligence
resolver maps them trivially.
"""

from __future__ import annotations

import re


_DATE = re.compile(
    r"^\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}[/-][A-Za-z]{3}[/-]\d{2,4})"
)
_TIME = re.compile(r"\d{1,2}:\d{2}")
_NUM = re.compile(r"^-?\d{1,3}(?:,\d{3})*(?:\.\d+)?$|^-?\d+(?:\.\d+)?$")
_LONGDIGIT = re.compile(r"^\d{8,}$")


def _to_float(v):
    try:
        return float(str(v).replace(",", "").strip())
    except Exception:
        return None


class ContentColumnProfiler:

    MIN_DATA_ROWS = 3

    def infer(self, grid: list[list]) -> dict:
        data_rows = [r for r in grid if self._is_data_row(r)]
        if len(data_rows) < self.MIN_DATA_ROWS:
            return {"rows": [], "assignment": {}, "reason": "too_few_data_rows"}

        ncols = max(len(r) for r in data_rows)
        cols = {c: [self._cell(r, c) for r in data_rows] for c in range(ncols)}
        feats = {c: self._profile(cols[c]) for c in range(ncols)}

        assigned: dict[int, str] = {}

        # 1) date: highest date ratio, prefer pure date over datetime
        date_c = self._pick(
            feats, lambda f: f["date"] > 0.6,
            key=lambda f: (f["date"], -f["time"]),
        )
        if date_c is not None:
            assigned[date_c] = "date"

        # 2) balance: numeric, decimals, almost always present (running balance)
        bal_c = self._pick(
            feats, lambda f: f["num"] > 0.7 and f["nonempty"] > 0.8,
            key=lambda f: (f["decimal"], f["nonempty"]),
            exclude=set(assigned),
        )
        if bal_c is not None:
            assigned[bal_c] = "balance"

        # 3) debit/credit: remaining numeric "amount-like" cols (many zeros)
        amount_cols = [
            c for c, f in feats.items()
            if c not in assigned and f["num"] > 0.7 and f["zeroish"] > 0.2
        ]
        debit_c, credit_c = self._assign_debit_credit(
            amount_cols, cols, bal_c, data_rows
        )
        if debit_c is not None:
            assigned[debit_c] = "debit"
        if credit_c is not None:
            assigned[credit_c] = "credit"

        # 4) ref_no: long digit runs
        ref_c = self._pick(
            feats, lambda f: f["longdigit"] > 0.3,
            key=lambda f: f["longdigit"], exclude=set(assigned),
        )
        if ref_c is not None:
            assigned[ref_c] = "ref_no"

        # 5) narration: longest average text among non-numeric columns
        narr_c = self._pick(
            feats, lambda f: f["num"] < 0.4 and f["avg_len"] > 0,
            key=lambda f: f["avg_len"], exclude=set(assigned),
        )
        if narr_c is not None:
            assigned[narr_c] = "narration"

        # Require a minimally useful table: a date AND (balance or an amount).
        have_amount = "balance" in assigned.values() or \
            "debit" in assigned.values() or "credit" in assigned.values()
        if "date" not in assigned.values() or not have_amount:
            return {"rows": [], "assignment": {}, "reason": "weak_inference"}

        rows = []
        for r in data_rows:
            row = {}
            for c, field in assigned.items():
                val = self._cell(r, c)
                row[field] = val if val != "" else None
            rows.append(row)

        return {
            "rows": rows,
            "assignment": {c: f for c, f in assigned.items()},
            "reason": "content_inferred",
        }

    # ------------------------------------------------------------------ #

    def _assign_debit_credit(self, amount_cols, cols, bal_c, data_rows):
        if not amount_cols:
            return None, None
        if bal_c is None:
            # no balance reference: assume positional debit-before-credit
            amount_cols = sorted(amount_cols)
            d = amount_cols[0] if amount_cols else None
            c = amount_cols[1] if len(amount_cols) > 1 else None
            return d, c

        balances = [_to_float(self._cell(r, bal_c)) for r in data_rows]
        scores = {}  # col -> (down_hits, up_hits)
        for col in amount_cols:
            down = up = 0
            prev = None
            for i, r in enumerate(data_rows):
                amt = _to_float(self._cell(r, col))
                bal = balances[i]
                if amt and amt != 0 and bal is not None and prev is not None:
                    if bal < prev:
                        down += 1
                    elif bal > prev:
                        up += 1
                if bal is not None:
                    prev = bal
            scores[col] = (down, up)

        debit_c = max(amount_cols, key=lambda c: scores[c][0] - scores[c][1],
                      default=None)
        credit_c = max(amount_cols, key=lambda c: scores[c][1] - scores[c][0],
                       default=None)
        if debit_c == credit_c:
            # only one amount column distinguishable
            d, u = scores[debit_c]
            return (debit_c, None) if d >= u else (None, debit_c)
        return debit_c, credit_c

    def _profile(self, vals):
        n = len(vals) or 1
        nonempty = [v for v in vals if v != ""]
        ne = len(nonempty) or 1
        date_hits = sum(1 for v in nonempty if _DATE.match(v))
        time_hits = sum(1 for v in nonempty if _TIME.search(v))
        num_hits = sum(1 for v in nonempty if _NUM.match(v))
        dec_hits = sum(1 for v in nonempty if _NUM.match(v) and "." in v)
        zero_hits = sum(1 for v in nonempty
                        if _to_float(v) in (0.0, None) or v in ("0", "0.0"))
        longdigit = sum(1 for v in nonempty if _LONGDIGIT.match(v))
        avg_len = sum(len(v) for v in nonempty) / ne
        return {
            "date": date_hits / ne,
            "time": time_hits / ne,
            "num": num_hits / ne,
            "decimal": dec_hits / ne,
            "zeroish": zero_hits / ne,
            "longdigit": longdigit / ne,
            "avg_len": avg_len,
            "nonempty": len(nonempty) / n,
        }

    def _pick(self, feats, predicate, key, exclude=frozenset()):
        cands = [c for c, f in feats.items()
                 if c not in exclude and predicate(f)]
        if not cands:
            return None
        return max(cands, key=lambda c: key(feats[c]))

    def _is_data_row(self, row):
        cells = [self._cell(row, i) for i in range(len(row))]
        text = " ".join(cells)
        return bool(_DATE.search(text) or re.search(r"\d+\.\d{2}", text))

    @staticmethod
    def _cell(row, c):
        if c < len(row) and row[c] is not None:
            return re.sub(r"\s+", " ", str(row[c]).replace("\n", " ")).strip()
        return ""
