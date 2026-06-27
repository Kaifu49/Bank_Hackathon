import re


class AmountNormalizer:

    def normalize(
        self,
        value
    ):

        if value is None:
            return None

        value = str(value)

        value = re.sub(
            r"[₹,\s]",
            "",
            value
        )

        value = value.replace(
            "INR",
            ""
        )

        value = value.replace(
            "Rs",
            ""
        )

        try:

            return float(value)

        except:

            return None