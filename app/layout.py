from dash import dcc, html


class Layout:
    def __init__(self):
        pass
        #self.colleagues_list = dropdown_lists.colleague_list
        self.product_project_list = None

    def generate(
        self,
    ):
        layout = html.Div(
            [
                html.Link(
                    rel="stylesheet",
                    href="https://fonts.googleapis.com/css?family=Open+Sans",
                    ),
                html.Div(
                    [
                        html.Div([
                            dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
                            html.Div(
                                html.Button('Reler planilhas', id='update-button'), 
                                style={"width": "fit-content"}),
                            # This style must be set here. If set in .css, callback funciton wont get it
                            html.Div(html.Div(id='progress-text'),
                                id='update-bar-loading', 
                                style={
                                    'width': '0%', 
                                    'height': 'fit-content', 
                                    'backgroundColor': 'green'}),
                        ],
                            id="update-area"),
                        html.H1("Visualizador dos Apontamentos",
                            id="title",
                            ),
                        self.date_picker(),
                        self.dropdown_lists(),
                        dcc.Graph(id="histogram"),
                    ]),
                # Commitment Histogram
                html.Div(
                    [
                        html.H1("Team Commitment", id="histogram-commitment-title"),
                        dcc.Graph(id="histogram-commitment"),
                    ],
                    id="histogram-commitment-container"
                )
            ]
        )
        return layout

    def date_picker(
        self,
    ):
        div = html.Div(
            [
                html.P("Horas despendidas no período considerado:",
                    id="subtitle"),
                dcc.DatePickerRange(
                    min_date_allowed="2022-01-01",
                    max_date_allowed="2022-12-31",
                    start_date="2022-01-01",
                    end_date="2022-12-31",
                    display_format='DD/MM/YYYY',
                    id="date-picker",
                ),
            ]
        )

        return div

    def dropdown_lists(
        self,
    ):
        return html.Div(
            [
                self.dropdown_list("Pessoa", "colleague-dropdown", [], "50%"),
                self.dropdown_list("Projeto", "project-dropdown", [], "100%"),
                self.dropdown_list("Produto", "product-dropdown", [], "100%"),
            ],
            id="dropdown-container-div")

    def dropdown_list(self, title, id, options, ratio):
        return html.Div(
            [
                html.P(title, 
                    className="dropdown-title"), 
                dcc.Dropdown(
                    id=id,
                    className="dropdown-list",
                    options=options,
                    value=None,
                    clearable=True,
                    searchable=True)
                ],
                className="dropdown-container", 
            style={"width": ratio})
