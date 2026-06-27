from services.neo4j_client import (
    Neo4jClient
)


class AccumulationDetector:

    def __init__(self):

        self.neo4j = Neo4jClient()

    def top_accumulation_accounts(
        self,
        limit=10
    ):

        query = """
        MATCH
        ()-[r:TRANSFERRED_TO]->
        (a)

        RETURN

        a.id AS account,

        SUM(
            r.total_amount
        ) AS total_received,

        COUNT(r)
        AS sender_count

        ORDER BY
        total_received DESC

        LIMIT $limit
        """

        with self.neo4j.driver.session() as session:

            result = session.run(
                query,
                {
                    "limit":
                        limit
                }
            )

            accounts = []

            for record in result:

                accounts.append(
                    {
                        "account":
                            record[
                                "account"
                            ],

                        "total_received":
                            record[
                                "total_received"
                            ],

                        "sender_count":
                            record[
                                "sender_count"
                            ]
                    }
                )

            return accounts