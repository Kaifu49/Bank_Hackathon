import re


PERSON_PATTERNS = [

    r"TRANSFER TO ([A-Z ]+)",

    r"SENT TO ([A-Z ]+)",

    r"PAID TO ([A-Z ]+)"
]


class PersonExtractor:

    def extract(
        self,
        text
    ):

        found = []

        upper = text.upper()

        for pattern in PERSON_PATTERNS:

            matches = re.findall(
                pattern,
                upper
            )

            found.extend(
                matches
            )

        return found