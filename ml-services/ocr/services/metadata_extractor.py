import re


class MetadataExtractor:

    def extract(
        self,
        text: str
    ):

        return {

            "account_number":
                self.extract_account(
                    text
                ),

            "ifsc":
                self.extract_ifsc(
                    text
                )
        }

    def extract_account(
        self,
        text
    ):

        match = re.search(
            r"\b\d{9,18}\b",
            text
        )

        return (
            match.group(0)
            if match
            else None
        )

    def extract_ifsc(
        self,
        text
    ):

        match = re.search(
            r"[A-Z]{4}0[A-Z0-9]{6}",
            text
        )

        return (
            match.group(0)
            if match
            else None
        )