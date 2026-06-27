"""
Column Intelligence — data-driven, bank-agnostic header resolution.

Replaces the naive substring `header_mapper.COLUMN_MAPPINGS` with a *scored*
resolver that generalizes across every bank/layout in the real evaluation
dataset (see docs/docs/Consolidated_Bank_Data.xlsx).

Design goals (per BACKEND_GAP_ANALYSIS_AND_ROADMAP.md, Phase 1):
  - No bank-specific or layout-specific code. All knowledge lives in the
    declarative SYNONYMS table below, derived from observed real headers.
  - Every source header maps to AT MOST one canonical field, and every
    canonical field takes its single best-scoring header (no silent collisions
    like "Value Date" overwriting "Txn Date").
  - Distinguishes split debit/credit layouts from single signed-amount layouts.
  - Emits a confidence score per mapping so downstream stages can flag
    low-confidence extractions instead of silently trusting them.

Canonical fields:
  date, value_date, narration, ref_no, debit, credit, balance, amount,
  txn_type, account
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


# --------------------------------------------------------------------------
# Knowledge base: canonical field -> weighted match rules.
#
# Each rule is (matcher, weight) where matcher is checked against the
# normalized header. Higher weight wins. "exact" rules (full-string equality)
# always beat "contains" rules so that e.g. a column literally named "DATE"
# is preferred as `date` over a "VALUE DATE" column.
#
# Weights:
#   EXACT  = 100  full normalized-string equality
#   STRONG =  60  distinctive token/phrase (low false-positive risk)
#   WEAK   =  30  generic token (needs no stronger competitor)
# --------------------------------------------------------------------------
EXACT, STRONG, WEAK = 100, 60, 30


def _norm(text: str) -> str:
    """Normalize a raw header cell into a comparable token string."""
    if text is None:
        return ""
    s = str(text)
    s = s.replace("_x000D_", " ").replace("\r", " ").replace("\n", " ")
    s = s.replace("﻿", " ")          # BOM
    s = s.lower()
    s = re.sub(r"[._/\\\-():*'\"`]", " ", s)   # punctuation -> space
    s = re.sub(r"\s+", " ", s).strip()
    return s


# field -> list of (exact_forms, strong_tokens, weak_tokens)
SYNONYMS: dict[str, dict[str, list[str]]] = {
    "date": {
        "exact": ["date", "txn date", "tran date", "transaction date",
                  "txn dt", "date", "tran date", "trans date", "posting date",
                  "tran date time", "date time"],
        "strong": ["txn date", "tran date", "transaction date", "txn dt"],
        "weak": ["date"],
    },
    "value_date": {
        "exact": ["value date", "post date", "value dt"],
        "strong": ["value date", "post date", "effective date"],
        "weak": [],
    },
    "narration": {
        "exact": ["narration", "description", "particulars", "tran particular",
                  "transaction details", "transaction particulars",
                  "tran particulars", "details", "remarks", "tran remarks",
                  "transaction remarks", "transaction description"],
        "strong": ["narration", "particular", "description",
                   "transaction detail", "remark", "transaction particular"],
        "weak": ["detail"],
    },
    "ref_no": {
        "exact": ["ref no", "reference", "reference no", "tran ref num",
                  "chqno", "chq no", "cheque no", "cheque number",
                  "instrument num", "instrument no", "tran id", "transaction id",
                  "txn id", "utr", "utr no", "ref", "chq num", "ctr batch no",
                  "instrument number", "reference number"],
        "strong": ["reference", "tran ref", "cheque", "chq", "instrument",
                   "tran id", "txn id", "utr", "ctr batch"],
        "weak": ["ref"],
    },
    "debit": {
        "exact": ["debit", "debits", "dr", "dr amt", "debit amt",
                  "debit amount", "withdrawal", "withdrawals", "withdrawal amt",
                  "withdrawal amount", "withdrawl", "withdrawals amt",
                  "amount debit", "debit dr"],
        "strong": ["debit", "withdrawal", "withdrawl", "dr amt", "dr amount"],
        "weak": ["dr"],
    },
    "credit": {
        "exact": ["credit", "credits", "cr", "cr amt", "credit amt",
                  "credit amount", "deposit", "deposits", "deposit amt",
                  "deposit amount", "amount credit", "credit cr"],
        "strong": ["credit", "deposit", "cr amt", "cr amount"],
        "weak": ["cr"],
    },
    "balance": {
        "exact": ["balance", "bal", "balance amt", "balance amount",
                  "closing balance", "available balance", "running balance",
                  "balance rs", "balance dr", "ledger balance"],
        "strong": ["balance"],
        "weak": ["bal"],
    },
    "amount": {
        "exact": ["amount", "amt", "transaction amount", "txn amount",
                  "tran amount"],
        "strong": ["transaction amount", "txn amount", "tran amount"],
        "weak": ["amount", "amt"],
    },
    "txn_type": {
        "exact": ["txn type", "tran type", "transaction type", "tran sub type",
                  "type", "dr cr", "drcr", "cr dr", "indicator"],
        "strong": ["transaction type", "tran type", "txn type", "dr cr",
                   "drcr"],
        "weak": ["type"],
    },
    "account": {   # statement holder's OWN account (metadata, not a counterparty)
        "exact": ["account no", "account number", "ac no", "a c no",
                  "account", "customer account", "acct no"],
        "strong": ["account no", "account number", "a c no", "ac no"],
        "weak": ["account"],
    },
    "sender_account": {   # explicit remitter/source column (investigation data)
        "exact": ["sender account", "from account", "source account",
                  "remitter account", "payer account", "sender", "remitter"],
        "strong": ["sender account", "from account", "source account",
                   "remitter"],
        "weak": ["sender"],
    },
    "receiver_account": {   # explicit beneficiary/destination column
        "exact": ["receiver account", "to account", "destination account",
                  "beneficiary account", "payee account", "receiver"],
        "strong": ["receiver account", "to account", "destination account",
                   "beneficiary account"],
        "weak": ["receiver"],
    },
}

# Confidence is derived from the winning weight.
_CONF = {EXACT: 0.99, STRONG: 0.85, WEAK: 0.55}


def _score(header_norm: str, field_name: str) -> int:
    """Best weight at which `header_norm` matches `field_name` (0 if none)."""
    rules = SYNONYMS[field_name]
    # exact full-string equality
    if header_norm in rules["exact"]:
        return EXACT
    best = 0
    for tok in rules["strong"]:
        if re.search(rf"(?:^| ){re.escape(tok)}(?: |$)", header_norm):
            best = max(best, STRONG)
    for tok in rules["weak"]:
        if re.search(rf"(?:^| ){re.escape(tok)}(?: |$)", header_norm):
            best = max(best, WEAK)
    return best


@dataclass
class ColumnMapping:
    """Resolved mapping: source header -> canonical field, with confidence."""
    mapping: dict[str, str] = field(default_factory=dict)        # source -> canonical
    confidence: dict[str, float] = field(default_factory=dict)   # source -> conf
    unmapped: list[str] = field(default_factory=list)
    amount_mode: str = "split"   # "split" (debit+credit) | "signed" (single amount)

    def overall_confidence(self) -> float:
        if not self.confidence:
            return 0.0
        return round(sum(self.confidence.values()) / len(self.confidence), 3)


def resolve_columns(headers: list[str]) -> ColumnMapping:
    """
    Resolve a list of raw header strings to canonical fields.

    Greedy by descending score with a one-to-one constraint: the single
    best (header, field) pair is assigned first, both are removed from the
    pools, and the process repeats. This prevents a generic "DATE" token from
    stealing the slot a more specific "VALUE DATE" header should own.
    """
    headers = [h for h in headers if h is not None and str(h).strip() != ""]
    norm = {h: _norm(h) for h in headers}

    # Build all candidate (score, header, field) triples.
    candidates: list[tuple[int, str, str]] = []
    for h in headers:
        for fname in SYNONYMS:
            sc = _score(norm[h], fname)
            if sc > 0:
                candidates.append((sc, h, fname))
    candidates.sort(key=lambda t: t[0], reverse=True)

    used_headers: set[str] = set()
    used_fields: set[str] = set()
    result = ColumnMapping()

    for sc, h, fname in candidates:
        if h in used_headers or fname in used_fields:
            continue
        result.mapping[h] = fname
        result.confidence[h] = _CONF[sc]
        used_headers.add(h)
        used_fields.add(fname)

    result.unmapped = [h for h in headers if h not in used_headers]

    # Amount-mode detection: if we found a single `amount` column but neither
    # debit nor credit, the layout is signed-amount; otherwise split.
    has_amount = "amount" in used_fields
    has_dr_cr = "debit" in used_fields or "credit" in used_fields
    result.amount_mode = "signed" if (has_amount and not has_dr_cr) else "split"

    return result
