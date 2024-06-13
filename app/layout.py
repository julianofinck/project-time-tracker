from dash import dcc, html


class Layout:
    def __init__(self):
        pass
        #self.colleagues_list = dropdown_lists.colleague_list
        self.product_project_list = None

    def generate(
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
            html.Div(id="update_area", children=[
                html.Div(id="update_bar_loading"),
                html.Button("Atualizar Dados", id="update-button")]),
            html.H1(
                id="title",
                children="Visualizador dos Apontamentos",
                style={"textAlign": "center", "color": "white"},
            ),
            self.date_picker(),
            self.dropdown_lists(),
            dcc.Graph(id="histogram"),
        ]

        # Style
        style = html.Div(children=childrens, style={})
        return links + [style]

    def date_picker(
        self,
    ):
        div = html.Div(
            [
                html.P(id="subtitle",children="Horas despendidas no período considerado:"),
                dcc.DatePickerRange(
                    id="date-picker",
                    min_date_allowed="2022-01-01",
                    max_date_allowed="2022-12-31",
                    start_date="2022-01-01",
                    end_date="2022-12-31",
                    display_format='DD/MM/YYYY',
                    #start_date_placeholder_text='D-M-Y'
                ),
            ],
            style={"width": "100%", "padding": "1%", "textAlign": "center"},
        )

        return div

    def dropdown_lists(
        self,
    ):
        options1 = [{"label": "Empty", "value": "Empty"}]
        return html.Div(
            [
                self.dropdown_list(
                    "Colaborador", "colleague-dropdown", options1, True, True, "50%"
                ),
                self.dropdown_list("Projeto", "project-dropdown", [], True, True, "100%"),
                self.dropdown_list("Produto", "product-dropdown", [], True, True, "100%"),
            ],
            style={
                "display": "flex",
                "flex-direction": "row",
                "justify-content": "space-evenly",
                #"flex-grow": 1,
                "width": "100%",
            },
        )

    def dropdown_list(self, title, id, options, clearable, searchable, ratio):
        # Title
        title = html.P(children=title, className="dropdown-title")

        # Dropdown list
        dropdown = dcc.Dropdown(
            id=id,
            className="dropdown-list",
            options=options,
            value=None,
            clearable=clearable,
            searchable=searchable,
            style={
                #"flex-grow": 1,
            },
        )
        return html.Div([title, dropdown], style={"width": ratio, "padding": "1%"})
