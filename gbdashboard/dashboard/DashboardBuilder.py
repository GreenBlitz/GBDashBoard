from typing import List

import networktables as nt


def generate_dashboard(name: str):
    table: nt.NetworkTable = nt.NetworkTables.getTable(name)
    subtables: List[str] = table.getSubTables()
    output = {}

    for curr_table_key in subtables:
        curr_table: nt.NetworkTable = table.getSubTable(curr_table_key)

        table_values = {}

        table_keys = curr_table.getKeys()
        for key in table_keys:
            table_values[key] = str(curr_table.getEntry(key))

        output[curr_table_key] = table_values

    return output
