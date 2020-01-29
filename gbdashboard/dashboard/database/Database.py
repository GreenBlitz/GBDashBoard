import os
import json
import sqlite3


class Database:

    def __init__(self, session_id, table_list, db=None):
        if db is None:
            self.database: sqlite3.Connection = sqlite3.Connection(Database.get_database_dir() + str(session_id) + ".db")
        else:
            self.database: sqlite3.Connection = db
        self.id = session_id
        self.table_list = []
        for table in table_list:
            self.add_table(table)

    DATABASE_DIRECTORY = "/gbdashboard/db/"
    ADD_TABLE = """
        CREATE TABLE IF NOT EXISTS dashname (
            param text PRIMARY KEY,
            time integer NOT NULL,
            value text
        );
    """
    ADD_VALUE = """
        INSERT into dashname(param, time, value)
        VALUES(?,?,?)
    """

    @staticmethod
    def generate_dashboard_query(dashboard):
        return Database.ADD_TABLE.replace("dashname", dashboard)

    @staticmethod
    def generate_value_query(dashboard):
        return Database.ADD_VALUE.replace("dashname", dashboard)

    @staticmethod
    def get_database_dir():
        return os.getcwd() + Database.DATABASE_DIRECTORY

    @staticmethod
    def load_config():
        with open(Database.get_database_dir() + "config.json", "r") as f:
            return json.load(f)

    def add_table(self, dashboard_name):
        if dashboard_name in self.table_list:
            return
        self.table_list.append(dashboard_name)
        c = self.database.cursor()
        try:
            c.execute(Database.generate_dashboard_query(dashboard_name))
        except sqlite3.Error as e:
            print(e)

    def insert_value(self, board, key, value, time):
        c = self.database.cursor()
        try:
            c.execute(Database.generate_value_query(board), (key, time, value))
        except sqlite3.Error as e:
            print(e)

    def flush(self):
        self.database.commit()

    '''
    The data here is as in generate_dashboard
    '''
    def update_database(self, data):
        pass

