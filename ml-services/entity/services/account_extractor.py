import re


ACCOUNT_PATTERN = re.compile(
    r"\b\d{9,18}\b"
)


class AccountExtractor:

    def extract(
        self,
        text: str
    ):

        if not text:
            return []

        return (
            ACCOUNT_PATTERN.findall(
                text
            )
        )