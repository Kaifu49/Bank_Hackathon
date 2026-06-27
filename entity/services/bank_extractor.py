import re

# IFSC first-4 prefix -> canonical bank name (data-driven, extensible).
IFSC_BANK = {
    "SBIN": "STATE BANK OF INDIA",
    "HDFC": "HDFC BANK",
    "ICIC": "ICICI BANK",
    "UTIB": "AXIS BANK",
    "YESB": "YES BANK",
    "KKBK": "KOTAK MAHINDRA BANK",
    "PUNB": "PUNJAB NATIONAL BANK",
    "BARB": "BANK OF BARODA",
    "CNRB": "CANARA BANK",
    "IDIB": "INDIAN BANK",
    "IOBA": "INDIAN OVERSEAS BANK",
    "UBIN": "UNION BANK OF INDIA",
    "MAHB": "BANK OF MAHARASHTRA",
    "IDFB": "IDFC FIRST BANK",
    "INDB": "INDUSIND BANK",
    "FINO": "FINO PAYMENTS BANK",
    "IPOS": "INDIA POST PAYMENTS BANK",
    "AIRP": "AIRTEL PAYMENTS BANK",
    "ESFB": "EQUITAS SMALL FINANCE BANK",
    "UJVN": "UJJIVAN SMALL FINANCE BANK",
    "JAKA": "JAMMU AND KASHMIR BANK",
    "DCBL": "DCB BANK",
    "RATN": "RBL BANK",
    "FDRL": "FEDERAL BANK",
    "SIBL": "SOUTH INDIAN BANK",
    "KVBL": "KARUR VYSYA BANK",
}

# Standalone bank-name strings (longest first so multi-word wins).
KNOWN_BANK_NAMES = sorted(set(IFSC_BANK.values()) | {
    "SBI", "HDFC", "ICICI", "AXIS", "KOTAK", "PAYTM PAYMENTS BANK",
    "BANK OF BARODA", "CANARA BANK", "YES BANK", "IDBI BANK",
}, key=len, reverse=True)

_IFSC = re.compile(r"\b([A-Z]{4})0[A-Z0-9]{6}\b")


class BankExtractor:
    """
    Resolve banks from (1) IFSC codes in the text (most reliable — derives the
    bank from the 4-letter prefix) and (2) explicit bank-name mentions.
    """

    def extract(self, text: str):
        if not text:
            return []
        upper = text.upper()
        found = []

        for m in _IFSC.finditer(upper):
            bank = IFSC_BANK.get(m.group(1))
            if bank:
                found.append(bank)

        for name in KNOWN_BANK_NAMES:
            if name in upper:
                found.append(name)

        return list(dict.fromkeys(found))
