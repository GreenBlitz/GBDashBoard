from gbdashboard.constants.dashboards import dashboards
import gbdashboard.dashboard.dashboard_builder as builder


def generate_webpage(dashboard):
    return builder.build_html_from_dashboard(builder.generate_dashboard(dashboard))


def build_dashboards(app):
    for dashboard in dashboards:
        app.add_url_rule("/board/" + dashboard, dashboards, lambda: generate_webpage(dashboard))

