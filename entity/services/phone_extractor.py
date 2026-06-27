import re

# Indian mobile: optional +91/91 prefix, then 10 digits starting 6-9.
# Require an explicit country prefix OR nearby context to avoid mistaking
# 10-digit account/reference numbers for phone numbers.
_WITH_PREFIX = re.compile(r"(?<!\d)(?:\+?91[\-\s]?)([6-9]\d{9})(?!\d)")
_CONTEXT = re.compile(
    r"(?:MOB(?:ILE)?|PHONE|CONTACT|PH\.?|CELL)[^0-9]{0,6}(?<!\d)([6-9]\d{9})(?!\d)",
    re.I,
)


class PhoneExtractor:
    """Extract phone numbers conservatively (prefix or context required)."""

    def extract(self, text: str):
        if not text:
            return []
        found = []
        for m in _WITH_PREFIX.finditer(text):
            found.append(m.group(1))
        for m in _CONTEXT.finditer(text):
            found.append(m.group(1))
        return list(dict.fromkeys(found))
