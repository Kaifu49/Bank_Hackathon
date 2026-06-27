"""
StandardizationService — converts raw extracted rows (arbitrary bank headers)
into canonical StandardizedTransactions, driven by the data-driven
column_intelligence resolver (bank/layout agnostic).

Backward compatible: `process(rows)` still returns the enriched transaction
list. `process_with_meta(rows)` additionally returns the resolved column
mapping + confidence so the API can surface extraction quality to the frontend.
"""

from services.column_intelligence import resolve_columns
from services.transaction_enricher import TransactionEnricher
from services.amount_normalizer import AmountNormalizer
from models.canonical_transaction import CanonicalTransaction


# numeric model fields and whether their sign is meaningful (balance only)
_NUMERIC_FIELDS = {"debit": False, "credit": False, "amount": False,
                   "balance": True}


# resolver canonical field -> CanonicalTransaction model field
RESOLVER_TO_MODEL = {
    "date": "date",
    "narration": "narration",
    "ref_no": "transaction_id",
    "debit": "debit",
    "credit": "credit",
    "balance": "balance",
    "amount": "amount",
    "txn_type": "txn_type",
    "account": "sender_account",
    # value_date intentionally dropped (no model field yet)
}


class StandardizationService:

    def __init__(self):
        self.enricher = TransactionEnricher()
        self.amount_norm = AmountNormalizer()

    # -- public API -------------------------------------------------------

    def process(self, rows):
        """Return only the enriched transaction list (legacy signature)."""
        transactions, _meta = self.process_with_meta(rows)
        return transactions

    def process_with_meta(self, rows):
        """Return (transactions, meta) where meta describes column resolution."""
        if not rows:
            return [], self._empty_meta()

        headers = self._collect_headers(rows)
        resolved = resolve_columns(headers)

        meta = {
            "column_mapping": resolved.mapping,           # source -> resolver field
            "confidence": resolved.confidence,            # source -> 0..1
            "overall_confidence": resolved.overall_confidence(),
            "amount_mode": resolved.amount_mode,
            "unmapped_columns": resolved.unmapped,
            "headers_seen": headers,
        }

        transactions = []
        for row in rows:
            if not isinstance(row, dict):
                continue  # skip stray non-dict rows (e.g. raw page text)
            canonical = self._build_canonical(row, resolved)
            enriched = self.enricher.enrich(canonical)
            transactions.append(enriched)

        meta["rows_in"] = len(rows)
        meta["rows_standardized"] = len(transactions)
        return transactions, meta

    # -- internals --------------------------------------------------------

    def _collect_headers(self, rows):
        """Union of header keys across all rows, preserving first-seen order."""
        seen = {}
        for row in rows:
            if isinstance(row, dict):
                for k in row.keys():
                    if k not in seen:
                        seen[k] = True
        return list(seen.keys())

    def _build_canonical(self, row, resolved):
        data = {}
        for source_col, resolver_field in resolved.mapping.items():
            model_field = RESOLVER_TO_MODEL.get(resolver_field)
            if model_field is None:
                continue
            data[model_field] = row.get(source_col)

        # Normalize numeric fields BEFORE constructing the float-typed model,
        # so values like "5,389.38Cr" / "(500.00)" / "₹1,200" become floats
        # instead of crashing pydantic. Balance keeps its sign (Dr/overdraft).
        for fld in ("debit", "credit", "balance"):
            if fld in data:
                signed = _NUMERIC_FIELDS[fld]
                data[fld] = self.amount_norm.normalize(data[fld], signed=signed)

        # Single signed-amount layout: keep the sign to derive direction, then
        # split into debit/credit so the downstream enricher behaves uniformly.
        if "amount" in data:
            signed_mode = resolved.amount_mode == "signed"
            amt = self.amount_norm.normalize(data["amount"], signed=signed_mode)
            data["amount"] = amt
            if signed_mode and amt is not None:
                if amt < 0:
                    data["debit"] = abs(amt)
                else:
                    data["credit"] = amt

        return CanonicalTransaction(**data)

    @staticmethod
    def _empty_meta():
        return {
            "column_mapping": {},
            "confidence": {},
            "overall_confidence": 0.0,
            "amount_mode": "split",
            "unmapped_columns": [],
            "headers_seen": [],
        }
