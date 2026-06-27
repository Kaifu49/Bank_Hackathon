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
from models.canonical_transaction import CanonicalTransaction


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
            canonical = self._build_canonical(row, resolved)
            enriched = self.enricher.enrich(canonical)
            transactions.append(enriched)

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

        # Signed single-amount layout: derive debit/credit from the sign so the
        # downstream enricher (which expects debit/credit) behaves uniformly.
        if resolved.amount_mode == "signed" and data.get("amount") is not None:
            amt = self._to_float(data.get("amount"))
            if amt is not None:
                if amt < 0:
                    data["debit"] = abs(amt)
                else:
                    data["credit"] = amt

        return CanonicalTransaction(**data)

    @staticmethod
    def _to_float(value):
        try:
            return float(str(value).replace(",", "").replace("₹", "").strip())
        except Exception:
            return None

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
