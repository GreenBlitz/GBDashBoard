import gbdashboard.dashboard.dashboard_builder as builder


def generate_webpage(dashboard):
    return builder.build_html_from_dashboard(builder.generate_dashboard(dashboard))


def build_dashboards(app):

    app.add_url_rule("/board/<dashboard>", "/board/", generate_webpage)
    app.add_url_rule("/board/<name>/update", "/board/update", builder.generate_dashboard)


