from dash import dash_table, dcc, html

from app.languages.translator import translator

EXTERNAL_LINKS = [
    "https://fonts.googleapis.com/css?family=Open+Sans",
]


def links_html(*links):
    return [html.Link(rel="stylesheet", href=link) for link in links]


class Layout:
    def __init__(self):
        pass
        # self.employees_list = dropdown_lists.employee_list
        self.product_project_list = None

    def generate(
        self,
    ):
        tab_commons = {
            "className": "tabs",
            "selected_className": "tabs--selected",
            "style": {"padding": "4px"},
            "selected_style": {"padding": "4px"},
        }
        layout = html.Div(
            links_html(*EXTERNAL_LINKS)
            + [
                # Selectors
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    translator.translate("Period of Interest"),
                                    id="dropdown-title",
                                    className="selector-title",
                                ),
                                dcc.DatePickerRange(
                                    min_date_allowed="2022-01-01",
                                    max_date_allowed="2022-12-31",
                                    start_date="2022-01-01",
                                    end_date="2022-12-31",
                                    display_format="DD/MM/YYYY",
                                    id="date-picker",
                                    className="selector-content",
                                    style={
                                        "width": "100%",
                                    },
                                ),
                            ],
                            id="date-picker-container",
                            className="selector",
                            style={"width": "30%"},
                        ),
                        self.dropdown_list(
                            translator.translate("Employee"),
                            "employee-selector",
                            "50%",
                        ),
                        self.dropdown_list(
                            translator.translate("Project"), "project-selector", "50%"
                        ),
                        self.dropdown_list(
                            translator.translate("Product"), "product-selector", "100%"
                        ),
                    ],
                    id="selectors-container",
                ),
                # Widgets & Cards
                html.Div(
                    [
                        # Spacer
                        html.Div(id="header-spacer"),
                        # Card - Working hours
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Interval(
                                            id="interval-component",
                                            interval=1000,
                                            n_intervals=0,
                                        ),
                                        html.Div(
                                            html.Button(
                                                translator.translate("Read Excels"),
                                                id="update-button",
                                            ),
                                            style={"width": "fit-content"},
                                        ),
                                        # This style must be set here. If set in .css, callback funciton wont get it
                                        html.Div(
                                            html.Div(id="progress-text"),
                                            id="update-bar-loading",
                                            style={
                                                "width": "0%",
                                                "height": "fit-content",
                                                "backgroundColor": "green",
                                            },
                                        ),
                                    ],
                                    id="update-area",
                                ),
                                html.H1(
                                    translator.translate("Workhours Viewer"),
                                    id="title",
                                    className="card-title",
                                ),
                                dcc.Graph(id="histogram"),
                                # Table
                                html.Div(
                                    [
                                        html.H1(
                                            translator.translate("Valid Records"),
                                            id="table-title",
                                            className="card-title",
                                        ),
                                        # Table
                                        html.Div(
                                            className="table",
                                            children=dash_table.DataTable(
                                                id="valid-table",
                                                columns=[
                                                    {"name": i, "id": i}
                                                    for i in ["dummy"]
                                                ],
                                                data=["dummy"],
                                                page_size=10,
                                                style_table={
                                                    "width": "100%",
                                                    "overflowX": "auto",
                                                    "height": "400px",
                                                },
                                                style_cell={
                                                    "textAlign": "left",
                                                    "padding": "5px",
                                                    "whiteSpace": "normal",
                                                    "overflow": "hidden",
                                                    "textOverflow": "ellipsis",
                                                },
                                                style_header={
                                                    "backgroundColor": "rgb(230, 230, 230)",
                                                    "fontWeight": "bold",
                                                },
                                            ),
                                        ),
                                    ],
                                    id="valid-table-container",
                                    className="card2",
                                ),
                            ],
                            id="main-analysis",
                            className="card",
                        ),
                        # Card - Controller-table
                        html.Div(
                            [
                                html.H1(
                                    translator.translate("Invalid Records"),
                                    id="controller-title",
                                    className="card-title",
                                ),
                                # Table
                                html.Div(
                                    className="table",
                                    children=dash_table.DataTable(
                                        id="controller-table",
                                        columns=[
                                            {"name": i, "id": i} for i in ["dummy"]
                                        ],
                                        data=["dummy"],
                                        page_size=10,
                                        style_table={
                                            "width": "100%",
                                            "overflowX": "auto",
                                            "height": "400px",
                                        },
                                        style_cell={
                                            "textAlign": "left",
                                            "padding": "5px",
                                            "whiteSpace": "normal",
                                            "overflow": "hidden",
                                            "textOverflow": "ellipsis",
                                        },
                                        style_header={
                                            "backgroundColor": "rgb(230, 230, 230)",
                                            "fontWeight": "bold",
                                        },
                                    ),
                                ),
                            ],
                            id="controller-table-container",
                            className="card",
                        ),
                        # Card - Commitment Histogram
                        html.Div(
                            [
                                html.H1(
                                    translator.translate("Team Commitment"),
                                    id="histogram-commitment-title",
                                    className="card-title",
                                ),
                                dcc.Tabs(
                                    [
                                        dcc.Tab(
                                            label=translator.translate(
                                                "Last Filled Day"
                                            ),
                                            value="last-reported-day",
                                            **tab_commons,
                                        ),
                                        dcc.Tab(
                                            label=translator.translate("Boxplot"),
                                            value="boxplot",
                                            **tab_commons,
                                        ),
                                        dcc.Tab(
                                            label=translator.translate(
                                                "Worked/Elapsed"
                                            ),
                                            value="elapsed-reported",
                                            **tab_commons,
                                        ),
                                    ],
                                    id="tabs-container",
                                    value="last-reported-day",
                                ),
                                dcc.Graph(id="histogram-commitment"),
                            ],
                            id="histogram-commitment-container",
                            className="card",
                        ),
                    ],
                    id="widgets-cards-container",
                ),
            ],
        )

        return layout

    def dropdown_list(self, title, id, ratio):
        return html.Div(
            [
                html.P(title, id=f"{id}-title", className="selector-title"),
                dcc.Dropdown(
                    id=id,
                    className="selector-content",
                    placeholder=translator.translate("Select..."),
                ),
            ],
            className="selector",
            style={"width": ratio},
        )
