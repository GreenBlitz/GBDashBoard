import os
import json
import sqlite3
import time

from gbdashboard.dashboard.dashboard_builder import generate_dashboard


class Database:

    def __init__(self, session_id, table_list, db=None):
        if db is None:
            self.database: sqlite3.Connection = sqlite3.Connection(
                Database.get_database_dir() + str(session_id) + ".db")
        else:
            self.database: sqlite3.Connection = db
        self.id = session_id
        self.table_list = []
        for table in table_list:
            initial_data = generate_dashboard(table)
            for subtable in initial_data:
                if subtable == "__name":
                    continue
                for param in initial_data[subtable]:
                    self.add_table(initial_data["__name"], subtable, param)

    DATABASE_DIRECTORY = "/gbdashboard/db/"
    ADD_TABLE = """
        CREATE TABLE IF NOT EXISTS "table_name" (
            time integer NOT NULL PRIMARY KEY,
            value text
        );
    """
    ADD_VALUE = """
        INSERT into "dashname"(time, value)
        VALUES(?,?)
    """
    GET_VALUE = """
        SELECT * FROM "__1"
    """

    @staticmethod
    def generate_dashboard_query(table_name):
        return Database.ADD_TABLE.replace("table_name", table_name)

    @staticmethod
    def generate_value_query(table_name):
        return Database.ADD_VALUE.replace("dashname", table_name)

    @staticmethod
    def generate_get_query(dashboard, subtale, key):
        return Database.GET_VALUE.replace("__1", dashboard + "_" + subtale + "_" + key)

    @staticmethod
    def get_database_dir():
        return os.getcwd() + Database.DATABASE_DIRECTORY

    @staticmethod
    def load_config():
        with open(Database.get_database_dir() + "config.json", "r") as f:
            return json.load(f)

    def add_table(self, dashboard_name, subtable, param):
        full_name = dashboard_name + "_" + subtable + "_" + param
        if full_name in self.table_list:
            return
        self.table_list.append(full_name)
        c = self.database.cursor()
        try:
            c.execute(Database.generate_dashboard_query(full_name))
        except sqlite3.Error as e:
            print(e)

    def insert_value(self, board, subboard, key, value, time):
        c = self.database.cursor()
        try:
            c.execute(Database.generate_value_query(board + "_" + subboard + "_" + key), (time, value))
        except sqlite3.Error as e:
            print(e)

    def get_parameter_timeline(self, table, subtable, key):
        c = self.database.cursor()
        try:
            c.execute(Database.generate_get_query(table, subtable, key))
        except sqlite3.Error as e:
            print(e)
            return []
        return c.fetchall()

    def flush(self):
        self.database.commit()

    '''
    The data here is as in generate_dashboard
    '''

    def update_database(self, data):

        for subtable in data:
            if subtable == "__name":
                continue
            for param in data[subtable]:
                self.add_table(data["__name"], subtable, param)
                self.insert_value(data["__name"], subtable, param,
                                  str(data[subtable][param]), int(time.time()*1000))

