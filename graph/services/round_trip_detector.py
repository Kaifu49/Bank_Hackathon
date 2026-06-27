from services.neo4j_client import (
    Neo4jClient
)


class RoundTripDetector:

    def __init__(self):

        self.neo4j = Neo4jClient()

    def detect_cycles(self):

        query = """
        MATCH p=
        (a:Account)
        -[:TRANSFERRED_TO*2..8]->
        (a)

        RETURN p
        LIMIT 100
        """

        with self.neo4j.driver.session() as session:

            result = session.run(query)

            cycles = []

            for record in result:

                path = record["p"]

                nodes = []

                for node in path.nodes:

                    nodes.append(
                        node["id"]
                    )

                cycles.append(nodes)

            return cycles