import os 
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class TimescaleDB(object):
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="postgres",
            user="panickyRaisins4@gardendb-rl",
            password=os.environ.get("tsdb_password"),
            host="gardendb-rl.postgres.database.azure.com"
        )

    def insert_sensor_records(self, records):
        with self.conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO sensor_data (timestamp, category, value)
                VALUES %s
                """,
                records,
            )
            self.conn.commit()
            print("Inserted into TimescaleDB")