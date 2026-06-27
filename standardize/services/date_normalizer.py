from dateutil import parser


class DateNormalizer:

    def normalize(
        self,
        value
    ):

        if not value:
            return None

        try:

            return (
                parser
                .parse(
                    str(value),
                    fuzzy=True
                )
                .strftime(
                    "%Y-%m-%d"
                )
            )

        except:

            return value