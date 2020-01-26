from typing import List, Dict

import networktables as nt
from bs4 import BeautifulSoup
import time

from gbdashboard.constants.net import ROBORIO_IP

NETWORK_TABLE_STARTED = False

SUB_TABLE_STYLE = "width:100%; \
            border:2px solid green"
HEADER_STYLE = "font-size: 30px"
TEXT_BOX_STYLE = "width: 100%;"
CELL_STYLE = "width: 1%; white-space: nowrap"


def init_network_tables():
    global NETWORK_TABLE_STARTED

    if not NETWORK_TABLE_STARTED:
        nt.NetworkTables.initialize(ROBORIO_IP)
        print("[DEBUG] Starting network table server...")
        time.sleep(0.5)  # Wait for connection to actually init itself
        print("[DEBUG] Started network table server.")
        NETWORK_TABLE_STARTED = True


def generate_row():
    pass


def generate_subtable(html_base, subtable_name, subtable_data):
    parent_tag = html_base.new_tag("th")
    subtable_tag = html_base.new_tag("table", style=SUB_TABLE_STYLE, id=subtable_name)

    title_tag = html_base.new_tag("tr")
    title = BeautifulSoup("<tr> \
                            <th> <b>Variable Name</b> </th> \
                            <th> <b>Variable Value</b> </th> \
                            <th>  </th> \
                        </tr>")
    title_tag.append(title)
    subtable_tag.append(title_tag)

    for data_point in sorted(subtable_data):
        data_tag = html_base.new_tag("tr", id=subtable_name + "->" + data_point)

        data_name_tag = html_base.new_tag("th", style=CELL_STYLE)
        data_name_tag.string = data_point

        data_value_tag = html_base.new_tag("th", style=CELL_STYLE)
        text_box_value_tag = html_base.new_tag("textarea", readonly="", style=TEXT_BOX_STYLE)
        text_box_value_tag.string = subtable_data[data_point]
        data_value_tag.append(text_box_value_tag)

        option_tag = html_base.new_tag("th", style=CELL_STYLE)
        option_tag.string = "temp"

        data_tag.append(data_name_tag)
        data_tag.append(data_value_tag)
        data_tag.append(option_tag)

        subtable_tag.append(data_tag)

    parent_tag.append(subtable_tag)
    return parent_tag


def generate_dashboard(name: str):
    init_network_tables()

    table: nt.NetworkTable = nt.NetworkTables.getTable(name)
    subtables: List[str] = table.getSubTables()
    output = {}

    table_values = {}

    table_keys = sorted(table.getKeys())
    for key in table_keys:
        table_values[key] = str(table.getEntry(key).get())

    output["parent"] = table_values

    for curr_table_key in subtables:
        curr_table: nt.NetworkTable = table.getSubTable(curr_table_key)

        table_values = {}

        table_keys = curr_table.getKeys()
        for key in table_keys:
            table_values[key] = str(curr_table.getEntry(key).get())

        output[curr_table_key] = table_values

    output["__name"] = name

    return output


def build_html_from_dashboard(json_data: Dict):
    with open("./gbdashboard/html/templates/dashboardTemplate.html") as fp:
        html_base = BeautifulSoup(fp)

    header = html_base.find(id="tableName")
    header.string = json_data["__name"]

    headings = html_base.find(id="headings")

    subtable_names = sorted(json_data)
    subtable_names.remove("parent")
    subtable_names.remove("__name")
    subtable_names = ["parent"] + subtable_names

    for table_name in subtable_names:
        new_tag = html_base.new_tag("th", style=HEADER_STYLE)
        new_tag.string = table_name
        headings.insert(0, new_tag)

    data = html_base.find(id="subtables")
    for table_name in subtable_names:
        data.insert(0, generate_subtable(html_base, table_name, json_data[table_name]))

    return str(html_base)


def test_everything():
    data = generate_dashboard("SmartDashboard")
    print(build_html_from_dashboard(data))

