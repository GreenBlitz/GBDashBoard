from typing import List

from gbdashboard.dashboard.dashboard_builder import generate_dashboard


def update_database(table_list: List[str]):
    for table_name in table_list:
        data = generate_dashboard(table_name)



