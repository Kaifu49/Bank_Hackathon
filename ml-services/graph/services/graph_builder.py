from services.neo4j_client import (
    Neo4jClient
)


class GraphBuilder:

    def __init__(self):

        self.neo4j = Neo4jClient()

    def build(
        self,
        transactions
    ):

        for txn in transactions:

            sender = (
                txn.get("sender_account")
                or txn.get("sender")
            )

            receiver = (
                txn.get("receiver_account")
                or txn.get("receiver")
            )

            amount = txn["amount"]

            date = txn["date"]

            query = """
MERGE (s:Account {
    id:$sender
})

MERGE (r:Account {
    id:$receiver
})

MERGE (s)-[t:TRANSFERRED_TO]->(r)

ON CREATE SET

    t.total_amount = $amount,
    t.transaction_count = 1,
    t.first_date = $date,
    t.last_date = $date

ON MATCH SET

    t.total_amount =
        COALESCE(
            t.total_amount,
            0
        ) + $amount,

    t.transaction_count =
        COALESCE(
            t.transaction_count,
            0
        ) + 1,

    t.last_date = $date
"""

            self.neo4j.execute(
                query,
                {
                    "sender": sender,
                    "receiver": receiver,
                    "amount": amount,
                    "date": date
                }
            )