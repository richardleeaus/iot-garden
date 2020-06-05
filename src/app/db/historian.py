import os 
import psycopg2
import logging
from psycopg2.extras import execute_values
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
logger = logging.getLogger(__name__)


class TimescaleDB(object):
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.environ.get("tsdb_dbname"),
            user=os.environ.get("tsdb_user"),
            password=os.environ.get("tsdb_password"),
            host=os.environ.get("tsdb_host")
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
            logger.info("Inserted into TimescaleDB")