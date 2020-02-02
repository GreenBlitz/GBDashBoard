import sqlite3

import matplotlib.pyplot as plt

from gbdashboard.dashboard.database import Database

SESSION_ID = 1

PATH = f"./db/{SESSION_ID}.db"

def plot_db(dashboard, subtable, value, start_time, end_time):
    conn = sqlite3.Connection(PATH)
    database =Database(SESSION_ID, None, db=conn)
    data = database.get_parameter_timeline(table=dashboard, subtable=subtable, key=value)
    target_data = filter(lambda x: start_time < x[1] < end_time, data)
    time_values = []
    values = []
    for i in target_data:
        time_values.append(i[1])
        values.append(i[2])
    plt.plot(time_values, values)
    plt.ylabel(value)
    plt.xlabel("time")
    plt.show()


def main():
    plot_db("SmartDashboard", "")