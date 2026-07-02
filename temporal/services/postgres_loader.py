import pandas as pd
import psycopg2


class PostgresLoader:

    def __init__(self):

        self.conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="finintel",
            user="postgres",
            password="postgres"
        )
        self.conn.autocommit = True

    def load_latest_statement_transactions(
        self
    ):

        query = """
        SELECT
            sender_account,
            receiver_account,
            amount,
            txn_type,
            date,
            statement_id

        FROM transactions

        WHERE statement_id = (

            SELECT id
            FROM statements
            ORDER BY upload_time DESC
            LIMIT 1

        )

        AND is_valid = true
        AND sender_account IS NOT NULL
        """

        return pd.read_sql(
            query,
            self.conn
        )

    def load_statement_transactions(
        self,
        statement_id
    ):

        query = """
        SELECT
            sender_account,
            receiver_account,
            amount,
            txn_type,
            date,
            statement_id

        FROM transactions

        WHERE statement_id = %s

        AND is_valid = true
        AND sender_account IS NOT NULL
        """

        return pd.read_sql(
            query,
            self.conn,
            params=[statement_id]
        )