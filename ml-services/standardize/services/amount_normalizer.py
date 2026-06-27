import re


class AmountNormalizer:
    """
    Parse messy monetary strings from real bank statements into floats.

    Handles: thousands separators (``5,389.38``), currency symbols/words
    (``₹``, ``INR``, ``Rs``), surrounding whitespace, parenthesised negatives
    (``(500.00)``), trailing minus (``500.00-``), and crucially the Indian
    Cr/Dr balance suffix (``5,389.38Cr`` / ``120.00Dr``).

    Args:
        signed: when True (use for *balance* columns) a ``Dr`` suffix or a
            parenthesised/negative value yields a negative number. When False
            (use for debit/credit/amount columns) the magnitude is returned and
            the Cr/Dr marker is treated as a label only.
    """

    _CRDR = re.compile(r"\b(cr|dr)\b\.?$", re.I)

    def normalize(self, value, signed: bool = False):
        if value is None:
            return None

        s = str(value).strip()
        if s == "" or s.lower() in {"na", "n/a", "none", "null", "-"}:
            return None

        negative = False

        # parenthesised negative: (500.00)
        if s.startswith("(") and s.endswith(")"):
            negative = True
            s = s[1:-1]

        # trailing/leading Cr/Dr marker
        m = self._CRDR.search(s.replace(" ", ""))
        is_dr = False
        is_cr = False
        # detect on a space-tolerant copy
        compact = re.sub(r"\s+", "", s)
        crdr = re.search(r"(cr|dr)\.?$", compact, re.I)
        if crdr:
            marker = crdr.group(1).lower()
            is_dr = marker == "dr"
            is_cr = marker == "cr"
            compact = compact[: crdr.start()]
            s = compact

        # remove currency words/symbols FIRST (before stripping spaces, so the
        # word boundary around "Rs"/"INR" still exists), then separators/spaces
        s = re.sub(r"(?i)(inr|rs\.?|₹)", "", s)
        s = re.sub(r"[,\s]", "", s)

        # trailing minus: 500.00-
        if s.endswith("-"):
            negative = True
            s = s[:-1]
        if s.startswith("-"):
            negative = True
            s = s[1:]

        try:
            num = float(s)
        except (ValueError, TypeError):
            return None

        if signed:
            if is_dr or negative:
                return -abs(num)
            return abs(num)

        # unsigned magnitude (Cr/Dr is only a label for amount columns)
        return abs(num)
