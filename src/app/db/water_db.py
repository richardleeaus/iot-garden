import sqlite3
import os


class WaterDatabase(object):

    def __init__(self):
        file_path = os.path.dirname(os.path.realpath(__file__))
        self.connection = sqlite3.connect(file_path + '/watering.db')
        self.configure()

    def configure(self):
        c = self.connection.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS WATER_LOG (
                [water_datetime] datetime PRIMARY KEY,
                [water_ml] integer,
                [pump_on_seconds] integer
            )''')
        self.connection.commit()

    def create_water_log(self, water_ml, pump_on_seconds):
        c = self.connection.cursor()
        c.execute('''
            INSERT INTO WATER_LOG (water_datetime, water_ml, pump_on_seconds)
            VALUES(CURRENT_TIMESTAMP, {}, {})
            '''.format(water_ml, pump_on_seconds))
        self.connection.commit()

    def get_pump_seconds_duration_in_last(self, minutes):
        c = self.connection.cursor()
        c.execute('''
            SELECT SUM(ifnull(pump_on_seconds,0))
            FROM WATER_LOG
            WHERE water_datetime <
                time(CURRENT_TIMESTAMP,'-{} minutes')
            '''.format(minutes))
        value = c.fetchone()[0]
        print("Fetch sqlite3 value is: {}".format(value))
        return 0 if value is None else value
        
