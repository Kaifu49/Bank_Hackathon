import re

# UPI VPA: handle@psp  (e.g. meera@okicici, paytm.s1a7ffh@pty, rahul@ybl)
UPI_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]+@[A-Za-z][A-Za-z0-9]+")


class UPIExtractor:
    """Extract UPI VPAs, excluding email addresses (handle@domain.tld)."""

    def extract(self, text: str):
        if not text:
            return []
        found = []
        for m in UPI_PATTERN.finditer(text):
            # If the match is immediately followed by '.', it's an email
            # domain (e.g. banker@idfcfirstbank.com) -> skip.
            if m.end() < len(text) and text[m.end()] == ".":
                continue
            found.append(m.group(0))
        return list(dict.fromkeys(found))
