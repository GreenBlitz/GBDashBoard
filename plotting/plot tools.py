import sqlite3

import matplotlib.pyplot as plt
from gbdashboard.dashboard.dashboard_builder import get_all_network_tables
from gbdashboard.dashboard.database import Database

SESSION_ID = 2

PATH = f"./plotting_db/{SESSION_ID}.db"


def plot_db(dashboard, subtable, value, start_time, end_time):
    conn = sqlite3.Connection(PATH)
    database = Database(SESSION_ID, get_all_network_tables(), db=conn)
    data = database.get_parameter_timeline(table=dashboard, subtable=subtable, key=value)
    target_data = list(filter(lambda x: start_time <= x[1] <= end_time, data))
    target_data.sort(key=lambda x: x[1], reverse=False)
    time_values = []
    values = []
    for i in target_data:
        time_values.append(i[1])
        values.append(i[2])
    time_zero = time_values[0]
    for i in range(len(time_values)):
        time_values[i] -= time_zero
        values[i] = float(values[i])
    plt.plot(time_values, values)
    plt.ylabel(value)
    plt.xlabel("time")
    plt.show()


def main():
    plot_db("SmartDashboard", "parent", "Ang vel", 1574229233109, 1574229235036)


if __name__ == '__main__':
    main()
