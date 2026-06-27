from services.neo4j_client import (
    Neo4jClient
)


class InvestigationService:

    def __init__(self):

        self.neo4j = Neo4jClient()

    def investigate(
        self,
        account_id: str
    ):

        with self.neo4j.driver.session() as session:

            # ------------------------
            # Total Outflow
            # ------------------------

            outflow_result = session.run(
                """
                MATCH
                (a:Account {
                    id:$account
                })
                -[r:TRANSFERRED_TO]->
                ()

                RETURN
                COALESCE(
                    SUM(r.total_amount),
                    0
                ) AS total_outflow
                """,
                {
                    "account":
                        account_id
                }
            )

            total_outflow = (
                outflow_result
                .single()[
                    "total_outflow"
                ]
            )

            # ------------------------
            # Total Inflow
            # ------------------------

            inflow_result = session.run(
                """
                MATCH
                ()
                -[r:TRANSFERRED_TO]->
                (a:Account {
                    id:$account
                })

                RETURN
                COALESCE(
                    SUM(r.total_amount),
                    0
                ) AS total_inflow
                """,
                {
                    "account":
                        account_id
                }
            )

            total_inflow = (
                inflow_result
                .single()[
                    "total_inflow"
                ]
            )

            # ------------------------
            # Top Receivers
            # ------------------------

            receiver_result = session.run(
                """
                MATCH
                (a:Account {
                    id:$account
                })
                -[r:TRANSFERRED_TO]->
                (b)

                RETURN
                b.id AS receiver,
                r.total_amount AS amount

                ORDER BY
                amount DESC

                LIMIT 10
                """,
                {
                    "account":
                        account_id
                }
            )

            top_receivers = []

            for record in receiver_result:

                top_receivers.append(
                    {
                        "account":
                            record[
                                "receiver"
                            ],

                        "amount":
                            record[
                                "amount"
                            ]
                    }
                )

            # ------------------------
            # Top Senders
            # ------------------------

            sender_result = session.run(
                """
                MATCH
                (b)
                -[r:TRANSFERRED_TO]->
                (a:Account {
                    id:$account
                })

                RETURN
                b.id AS sender,
                r.total_amount AS amount

                ORDER BY
                amount DESC

                LIMIT 10
                """,
                {
                    "account":
                        account_id
                }
            )

            top_senders = []

            for record in sender_result:

                top_senders.append(
                    {
                        "account":
                            record[
                                "sender"
                            ],

                        "amount":
                            record[
                                "amount"
                            ]
                    }
                )

            # ------------------------
            # Direct Receiver Count
            # ------------------------

            receiver_count_result = session.run(
                """
                MATCH
                (a:Account {id:$account})
                -[:TRANSFERRED_TO]->
                (b)

                RETURN
                COUNT(DISTINCT b) AS cnt
                """,
                {
                    "account": account_id
                }
            )

            direct_receivers = (
                receiver_count_result
                .single()["cnt"]
            )


            sender_count_result = session.run(
                """
                MATCH
                (b)
                -[:TRANSFERRED_TO]->
                (a:Account {id:$account})

                RETURN
                COUNT(DISTINCT b) AS cnt
                """,
                {
                    "account": account_id
                }
            )

            direct_senders = (
                sender_count_result
                .single()["cnt"]
            )
            return {

                "account":
                    account_id,

                "total_outflow":
                    total_outflow,

                "total_inflow":
                    total_inflow,

                "direct_receivers":
                    direct_receivers,

                "direct_senders":
                    direct_senders,

                "top_receivers":
                    top_receivers,

                "top_senders":
                    top_senders,
            }