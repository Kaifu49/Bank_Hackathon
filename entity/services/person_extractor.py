import re

# Name that follows a UPI VPA + '/'  e.g. "meera@okicici/RADHA REKHA SAXENA"
_AFTER_VPA = re.compile(
    r"@[A-Za-z0-9]+/([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})"
)
# Explicit directional phrases
_DIRECTIONAL = [
    re.compile(r"TRANSFER TO ([A-Z][A-Z ]{2,})"),
    re.compile(r"SENT TO ([A-Z][A-Z ]{2,})"),
    re.compile(r"PAID TO ([A-Z][A-Z ]{2,})"),
]

# tokens that look like names but aren't
_STOPWORDS = {"UPI", "IMPS", "NEFT", "RTGS", "BANK", "LIMITED", "LTD", "BRANCH",
              "ATM", "CASH", "WITHDRAWAL", "PAYMENT", "TRANSFER", "CREDIT",
              "DEBIT", "SELF", "INDIA", "INR"}


class PersonExtractor:
    """Heuristic person-name extraction from cryptic bank narrations."""

    def extract(self, text):
        if not text:
            return []
        found = []

        for m in _AFTER_VPA.finditer(text):
            found.append(m.group(1).strip())

        upper = text.upper()
        for pat in _DIRECTIONAL:
            for m in pat.finditer(upper):
                found.append(m.group(1).strip())

        clean = []
        for name in found:
            tokens = [t for t in name.split() if t.upper() not in _STOPWORDS]
            if len(tokens) >= 2:                      # require >= 2 name parts
                clean.append(" ".join(tokens))
        return list(dict.fromkeys(clean))
