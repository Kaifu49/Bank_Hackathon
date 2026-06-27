import re

# Account number ONLY when preceded by an account-context keyword. Bare long
# digit runs in narrations are transaction references (UTR/RRN/batch), not
# accounts, and were previously polluting the entity set with false accounts.
_ACCOUNT_CONTEXT = re.compile(
    r"(?:A/?C|ACCOUNT|ACCT|BENEFICIARY|BENEF|REMITTER)[^0-9]{0,8}(\d{9,18})",
    re.I,
)


class AccountExtractor:
    """Extract account numbers using surrounding context (low false positives)."""

    def extract(self, text: str):
        if not text:
            return []
        return list(dict.fromkeys(
            m.group(1) for m in _ACCOUNT_CONTEXT.finditer(text)
        ))
