from services.merchant_dictionary import (
    KNOWN_MERCHANTS
)


class MerchantExtractor:

    def extract(
        self,
        text
    ):

        found = []

        if not text:
            return found

        upper = text.upper()

        for merchant in KNOWN_MERCHANTS:

            if merchant in upper:

                found.append(
                    merchant
                )

        return found