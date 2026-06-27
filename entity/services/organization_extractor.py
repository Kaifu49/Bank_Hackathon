KNOWN_ORGS = [

    "PAYTM",
    "PHONEPE",
    "GOOGLEPAY",
    "GOOGLE PAY",
    "AMAZON",
    "FLIPKART",
    "AIRTEL",
    "JIO",
    "SWIGGY",
    "ZOMATO"
]


class OrganizationExtractor:

    def extract(
        self,
        text
    ):

        if not text:
            return []

        text = text.upper()

        found = []

        for org in KNOWN_ORGS:

            if org in text:

                found.append(
                    org
                )

        return found