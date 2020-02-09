from flask import request
import networktables as nt

import gbdashboard.dashboard.dashboard_builder as builder


def generate_webpage(dashboard):
    return builder.build_html_from_dashboard(builder.generate_dashboard(dashboard))


def build_dashboards(app):
    @app.route('/board')
    def board():
        return builder.build_index()

    @app.route('/board/<dashboard>/senddata')
    def update(dashboard):
        subtable = request.args.get('subtable')
        key = request.args.get('key')
        value = request.args.get('value')

        table = nt.NetworkTables.getTable(dashboard)
        if subtable == "parent":
            subtable_: nt.NetworkTable = table
        else:
            subtable_: nt.NetworkTable = table.getSubTable(subtable)

        try:
            value = float(value)
            is_num = True
        except:
            value = str(value)
            is_num = False

        subtable_.putValue(key, value)

        return "Inseted " + str(value) + " to " + dashboard + " into subtable " + subtable + ". As number? " + str(is_num)



    app.add_url_rule("/board/<dashboard>", "/board/", generate_webpage)
    app.add_url_rule("/board/<name>/update", "/board/update", builder.generate_dashboard)
