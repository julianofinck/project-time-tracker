from dash import dcc, html, dash_table


class Layout:
    def __init__(self):
        pass
        #self.colleagues_list = dropdown_lists.colleague_list
        self.product_project_list = None

    def generate(
        self,
    ):
        tab_commons = {
                "className": "tabs", 
                "selected_className": "tabs--selected", 
                "style": {"padding": "4px"}, 
                "selected_style": {"padding": "4px"}
                }
        layout = html.Div([
            html.Link(rel="stylesheet", href="https://fonts.googleapis.com/css?family=Open+Sans",),

            # Main Histogram
            html.Div([
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
                html.H1("Visualizador de Apontamentos", id="title", className="card-title"),
                self.dropdown_lists(),
                html.Div([
                    html.P("Período de Interesse",
                        id="subtitle"),
                    dcc.DatePickerRange(
                        min_date_allowed="2022-01-01",
                        max_date_allowed="2022-12-31",
                        start_date="2022-01-01",
                        end_date="2022-12-31",
                        display_format='DD/MM/YYYY',
                        id="date-picker",
                    ),],),
                dcc.Graph(id="histogram"),
                ], id="main-analysis", 
                className="card"),

            # Controller-table
            html.Div(
                [
                    html.H1("Registros inválidos (Controller)", id="controller-title", className="card-title"),
                    dash_table.DataTable(
                        id='controller-table',
                        columns=[{"name": i, "id": i} for i in ["dummy"]],
                        data=["dummy"],
                        page_size=10,
                        style_table={'width': '100%', 'overflowX': 'auto', "height": "400px"},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '5px',
                            'whiteSpace': 'normal',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis'
                        },
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        }
                    ),
                ],
                id="controller-table-container",
                className="card"),

            # Commitment Histogram
            html.Div(
                [
                    html.H1("Compromisso da Equipe", id="histogram-commitment-title", className="card-title"),
                    dcc.Tabs([
                        dcc.Tab(label="Último Preenchimento", value="value1", **tab_commons),
                        dcc.Tab(label="1º Preenchimento", value="value2", **tab_commons),
                        dcc.Tab(label="FilledDays/Workdays", value="value3", **tab_commons),
                        dcc.Tab(label="Percentage", value="value4", **tab_commons),
                    ],
                        id="tabs-container"),
                    dcc.Graph(id="histogram-commitment"),
                ],
                id="histogram-commitment-container",
                className="card"),
            ],)
            
        return layout

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
                    id=f"{id}-title",
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
