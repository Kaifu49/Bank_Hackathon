import re

# Canonical IFSC: 4 letters + '0' + 6 alphanumerics (e.g. YESB0000419, BARB0KHOBAR)
IFSC_PATTERN = re.compile(r"\b([A-Z]{4}0[A-Z0-9]{6})\b")


class IFSCExtractor:
    """Extract IFSC codes from narration/reference text (bank-agnostic)."""

    def extract(self, text: str):
        if not text:
            return []
        return [m.group(1) for m in IFSC_PATTERN.finditer(text.upper())]
