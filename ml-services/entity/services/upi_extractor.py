import re


UPI_PATTERN = re.compile(
    r"[A-Za-z0-9._-]+@[A-Za-z]+"
)


class UPIExtractor:

    def extract(
        self,
        text: str
    ):

        if not text:
            return []

        return (
            UPI_PATTERN.findall(
                text
            )
        )