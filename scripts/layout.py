from dash import Dash, Input, Output, dcc, html


class Layout:
    def __init__(self, dropdown_lists):
        self.colleagues_list = dropdown_lists.colleague_list
        self.product_project_list = dropdown_lists.product_project_list

    def layout(
        self,
    ):
        layout = html.Div(self.main_properties())
        return layout

    def main_properties(
        self,
    ):
        # External links
        links = [
            html.Link(
                rel="stylesheet",
                href="https://fonts.googleapis.com/css?family=Open+Sans",
            ),
            html.Link(rel="stylesheet", href="assets/style.css"),
        ]

        # Components
        childrens = [
            html.Div(
                id="window-size-display",
                style={"display": "none", "visibility": "hidden"},
                children=[
                    "Current Window Size: Width: ",
                    html.Span(id="window-size-width"),
                    html.Span(id="window-size-height"),
                ],
            ),
            html.H1(
                children="Visualizador dos Apontamentos",
                style={"textAlign": "center", "color": "white"},
            ),
            self.date_picker(),
            dcc.Graph(id="histogram"),
            self.dropdown_lists(),
        ]

        # Style
        style = html.Div(children=childrens, style={})
        return links + [style]

    def date_picker(
        self,
    ):
        div = html.Div(
            [
                html.P(children="Horas despendidas no período considerado:"),
                dcc.DatePickerRange(
                    id="date-picker",
                    min_date_allowed="2022-01-01",
                    max_date_allowed="2022-12-31",
                    start_date="2022-01-01",
                    end_date="2022-12-31",
                ),
            ],
            style={"width": "100%", "padding": "1%", "textAlign": "center"},
        )

        return div

    def dropdown_lists(
        self,
    ):
        options1 = [{"label": i, "value": i} for i in self.colleagues_list]
        return html.Div(
            [
                self.dropdown_list(
                    "Colaborador", "colleague-dropdown", options1, True, True
                ),
                self.dropdown_list("Projeto", "project-dropdown", [], True, True),
                self.dropdown_list("Produto", "product-dropdown", [], True, True),
            ],
            style={
                "display": "flex",
                "flex-direction": "row",
                "justify-content": "space-evenly",
                "flex-grow": 1,
                "width": "100%",
            },
        )

    def dropdown_list(self, title, id, options, clearable, searchable):
        # Title
        title = html.P(children=title)

        # Dropdown list
        dropdown = dcc.Dropdown(
            id=id,
            className="dropdown-list",
            options=options,
            value=self.colleagues_list[0],
            clearable=clearable,
            searchable=searchable,
            style={
                "flex-grow": 1,
            },
        )
        return html.Div([title, dropdown], style={"width": "100%", "padding": "1%"})


class DropDownLists:
    def __init__(self, dfs):
        self.colleague_list = list(dfs.keys())
        self.product_project_list = {
            colleague: df[["Produto", "Projeto"]].drop_duplicates()
            for colleague, df in dfs.items()
        }
