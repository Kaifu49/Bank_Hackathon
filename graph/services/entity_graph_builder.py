from services.neo4j_client import (
    Neo4jClient
)


class EntityGraphBuilder:

    def __init__(self):

        self.neo4j = Neo4jClient()

    def build(
        self,
        transactions,
        entities
    ):

        # ------------------------
        # Transaction Nodes
        # ------------------------

        for txn in transactions:

            txn_id = (
                txn.get(
                    "reference_number"
                )
                or
                f"TXN_{hash(str(txn))}"
            )

            query = """
MERGE (
    t:Transaction {
        id:$txn_id
    }
)

SET
    t.date = $date,
    t.amount = $amount,
    t.txn_type = $txn_type,
    t.narration = $narration
"""

            self.neo4j.execute(
                query,
                {
                    "txn_id":
                        txn_id,

                    "date":
                        txn.get("date"),

                    "amount":
                        txn.get("amount"),

                    "txn_type":
                        txn.get("txn_type"),

                    "narration":
                        txn.get("narration")
                }
            )

        # ------------------------
        # Entity Nodes
        # ------------------------

        for entity in entities:

            canonical = (
                entity[
                    "canonical"
                ]
            )

            aliases = (
                entity.get(
                    "aliases",
                    []
                )
            )

            query = """
MERGE (
    e:Entity {
        id:$entity_id
    }
)

SET
    e.aliases = $aliases
"""

            self.neo4j.execute(
                query,
                {
                    "entity_id":
                        canonical,

                    "aliases":
                        aliases
                }
            )

        # ------------------------
        # INVOLVES Relationships
        # ------------------------

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
                    "narration"
                )
                or ""
            )

            for entity in entities:

                canonical = (
                    entity[
                        "canonical"
                    ]
                )

                if (
                    canonical.lower()
                    in narration.lower()
                ):

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