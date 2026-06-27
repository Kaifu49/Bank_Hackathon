from services.neo4j_client import (
    Neo4jClient
)


class MoneyFlowAnalyzer:

    def __init__(self):

        self.neo4j = Neo4jClient()

    def trace(
        self,
        source_account
    ):

        query = """
        MATCH p=
        (a:Account {
            id:$source
        })
        -[:TRANSFERRED_TO*1..5]->
        (b)

        RETURN p
        LIMIT 100
        """

        with self.neo4j.driver.session() as session:

            result = session.run(
                query,
                {
                    "source":
                        source_account
                }
            )

            paths = []

            for record in result:

                path = record["p"]

                nodes = []

                for node in path.nodes:

                    nodes.append(
                        node["id"]
                    )

                paths.append(nodes)

            return paths