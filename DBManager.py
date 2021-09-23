import os
import psycopg2


class DBManager:
    conn = None

    def __connect(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )

    def get_conn(self):
        if not self.conn:
            self.__connect()

        return self.conn
