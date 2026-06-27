KNOWN_BANKS = [

    "SBI",
    "STATE BANK OF INDIA",

    "HDFC",
    "HDFC BANK",

    "ICICI",
    "ICICI BANK",

    "AXIS",
    "AXIS BANK",

    "KOTAK",
    "KOTAK BANK",

    "PAYTM PAYMENTS BANK"
]


class BankExtractor:

    def extract(
        self,
        text
    ):

        if not text:
            return []

        text = text.upper()

        found = []

        for bank in KNOWN_BANKS:

            if bank in text:

                found.append(
                    bank
                )

        return found