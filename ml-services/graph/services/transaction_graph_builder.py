from services.neo4j_client import (
    Neo4jClient
)


class TransactionGraphBuilder:

    def __init__(self):

        self.neo4j = Neo4jClient()

    def build(
        self,
        transactions,
        entities
    ):

        # Create Transaction Nodes

        for txn in transactions:

            txn_id = (
                txn.get(
                    "reference_number"
                )
                or
                f"TXN_{hash(str(txn))}"
            )

            query = """
MERGE (t:Transaction {
    id:$txn_id
})

SET
    t.amount = $amount,
    t.date = $date,
    t.txn_type = $txn_type,
    t.debit_credit = $debit_credit,
    t.narration = $narration
"""

            self.neo4j.execute(
                query,
                {
                    "txn_id":
                        txn_id,
                    "amount":
                        txn.get("amount"),
                    "date":
                        txn.get("date"),
                    "txn_type":
                        txn.get("txn_type"),
                    "debit_credit":
                        txn.get("debit_credit"),
                    "narration":
                        txn.get("narration")
                }
            )

        # Create Entity Nodes

        for entity in entities:

            query = """
MERGE (e:Entity {
    id:$entity_id
})

SET
    e.aliases = $aliases
"""

            self.neo4j.execute(
                query,
                {
                    "entity_id":
                        entity[
                            "canonical"
                        ],
                    "aliases":
                        entity.get(
                            "aliases",
                            []
                        )
                }
            )

        # Create INVOLVES Relationships

        for txn in transactions:

            txn_id = (
                txn.get(
                    "reference_number"
                )
                or
                f"TXN_{hash(str(txn))}"
            )

            narration = (
                txn.get(
                    "narration",
                    ""
                )
            )

            for entity in entities:

                canonical = (
                    entity[
                        "canonical"
                    ]
                )

                if canonical in narration:

                    query = """
MATCH (
    t:Transaction {
        id:$txn_id
    }
)

MATCH (
    e:Entity {
        id:$entity_id
    }
)

MERGE
(t)-[:INVOLVES]->(e)
"""

                    self.neo4j.execute(
                        query,
                        {
                            "txn_id":
                                txn_id,
                            "entity_id":
                                canonical
                        }
                    )