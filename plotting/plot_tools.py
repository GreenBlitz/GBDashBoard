import sqlite3

import matplotlib.pyplot as plt
from gbdashboard.dashboard.dashboard_builder import get_all_network_tables
from gbdashboard.dashboard.database import Database

SESSION_ID = 1

PATH = f"../gbdashboard/db/{SESSION_ID}.db"


def plot_db(dashboard, subtable, value, start_time=0, end_time=None):
    conn = sqlite3.Connection(PATH)
    database = Database(SESSION_ID, get_all_network_tables(), db=conn)
    data = database.get_parameter_timeline(table=dashboard, subtable=subtable, key=value)
    if end_time is None:
        target_data = list(filter(lambda x: start_time <= x[0], data))
    else:
        target_data = list(filter(lambda x: start_time <= x[0] <= end_time, data))
    target_data.sort(key=lambda x: x[1], reverse=False)
    time_values = []
    values = []
    for i in target_data:
        time_values.append(i[0] / 1000.0)
        values.append(i[1])
    time_zero = time_values[0]
    for i in range(len(time_values)):
        time_values[i] -= time_zero
        if values[i] in ["True", "False"]:
            values[i] = 1.0 if values[i] == "True" else 0.0
        else:
            values[i] = float(values[i])
    plt.plot(time_values, values, 'rx-')
    plt.ylabel(value)
    plt.xlabel("time")
    plt.show()


def main():
    plot_db("Turret", "parent", "Angle from front deg", 0, None)


if __name__ == '__main__':
    main()
