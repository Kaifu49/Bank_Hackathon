"""Compact narration -> counterparty resolver (mirrors the graph engine's
logic) so the money trail can show WHERE each debit sent the money."""

import re

_UPI = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]+@[A-Za-z][A-Za-z0-9]+")
_NAME_AFTER_VPA = re.compile(
    r"@[A-Za-z0-9]+/([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})")
_MERCHANTS = ("PAYTM", "PHONEPE", "GOOGLE PAY", "GPAY", "AMAZON", "FLIPKART",
              "SWIGGY", "ZOMATO", "JIO", "AIRTEL")


def resolve(narration: str):
    narr = narration or ""
    if not narr:
        return None
    m = _UPI.search(narr)
    if m and not (m.end() < len(narr) and narr[m.end()] == "."):
        return m.group(0).lower()
    pm = _NAME_AFTER_VPA.search(narr)
    if pm:
        return pm.group(1).strip().upper()
    up = narr.upper()
    for mk in _MERCHANTS:
        if mk in up:
            return mk
    if "ATM" in up or "CASH" in up:
        return "CASH"
    return None
