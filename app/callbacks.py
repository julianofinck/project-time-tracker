import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Input, Output, State, clientside_callback
from .__init__ import app
from .extract import extractor
import datetime
import threading
import time


# Global progress variable
progress = 0
running_thread = False

# Espaço para calculos
a = dict()
for pessoa, df in extractor.data.items():
    try:
        min_ = df["Data"].min()
    except:
        min_ = None
    try:
        max_ = df["Data"].max()
    except:
        max_ = None
    a[pessoa] = (min_, max_)
result = pd.DataFrame(a).T
print(result.sort_values(1))
# Espaço para calculos




def update_data():
    
    # For the bar in frontend
    global progress
    extractor._get_colleagues()
    filename_colleagues = [(filename, colleague) for filename, colleagues in extractor.filename_colleagues.items() for colleague in colleagues ]
    total_iterations = len(filename_colleagues)

    # Set max intervals
    max_intervals = 3 #filename_colleagues
    clientside_callback(
        """
        function(data) {
            return MAX_INTERVALS;
        }
        """.replace("MAX_INTERVALS", str(max_intervals)),
        Output('interval-component', 'max_intervals'),
        [Input('interval-component', 'n_intervals')],
    )

    # If not specified, use all colleagues
    ti = time.time()
    data = dict()
    for i, (filename, colleague) in enumerate(filename_colleagues):
        data[colleague] = extractor._get_df(filename, colleague) 
        progress = (i + 1) / total_iterations * 100

    # TODO: stop interval

    extractor.data = data
    tf = time.time()
    print("Elapsed time:", int(tf - ti), "s")
    extractor.colleague_list = list(extractor.data.keys())

    extractor.product_project_list = {
        colleague: df[["Produto", "Projeto"]].drop_duplicates()
        for colleague, df in extractor.data.items()
    }

    extractor._save_state()
    return 0

# Callback to start the background process
@app.callback(
    Output('interval-component', 'disabled'),
    Output('update-button', 'n_clicks'),
    Output('update-bar-loading', 'style'),
    Output('progress-text', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('update-button', 'n_clicks'),
    State('update-bar-loading', 'style')
)
def start_update(n_intervals, n_clicks, style):
#def start_update(n_clicks):    
    global progress, running_thread

    style['width'] = f'{progress}%'

    if n_clicks not in (None, 0) and not running_thread:
        threading.Thread(target=update_data).start()
        running_thread = True
        return False, None, style, f'{int(progress)}%'
    elif running_thread and progress < 99:
        return False, None, style, f'{int(progress)}%'
    elif n_intervals > 10:
        running_thread = False
        progress = 0
        style['width'] = f'100%'
        return True, None, style, f'Atualizado!'
    else:
        return True, None, style, f''



# DatePickerRange
@app.callback(
    Output("date-picker", "min_date_allowed"),
    Output("date-picker", "max_date_allowed"),
    Output("date-picker", "start_date"),
    Output("date-picker", "end_date"),
    [Input("colleague-dropdown", "value")],
)
def update_date_picker(colleague):
    if colleague is None:
        return tuple(["2000-01-01T00:00:00Z"] * 4)
    
    df = extractor.data[colleague]
    return (
        df["Data"].min().strftime("%Y-%m-%d"),
        df["Data"].max().strftime("%Y-%m-%d"),
        df["Data"].min().strftime("%Y-%m-%d"),
        df["Data"].max().strftime("%Y-%m-%d"),
    )


# Histogram
@app.callback(
    Output("histogram", "figure"),
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("colleague-dropdown", "value"),
        Input("project-dropdown", "value"),
        Input("product-dropdown", "value"),
    ],
)
def update_histogram(start_date, end_date, colleague, project, product):
    # Create layout for histogram
    layout = go.Layout(
        xaxis=dict(tickangle=-35, tickfont=dict(size=8)),
        autosize=False,
        height=200,
        margin=dict(l=7, r=7, b=7, t=7, pad=0),
    )
    # TODO: Change the hardcoded "7" for something more responsive

    if colleague is None:
        hist_data = [
        go.Bar(
            x=["No selection"],
            y=[0],
            text=[""],
            hovertemplate=["No selection<extra></extra>"],
            marker=dict(
                color="#198238",  # Color hex code
            ),
        )]
    
        # Create figure
        figure = go.Figure(data=hist_data)
        return figure
    
    # Get the data accordingly
    df = extractor.data[colleague]

    # Filter data based on selected dates
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
    filtered_df = df[(df["Data"] >= start_datetime) & (df["Data"] <= end_datetime)]

    # Filter by project, show products
    groupby_field = "Projeto"
    mask = filtered_df["Projeto"].copy()
    mask.loc[:] = True
    if project not in (None, "Empty"):
        mask = mask & (filtered_df["Projeto"] == project)
        groupby_field = "Produto"
        if project == "CODEX":
            groupby_field = "Atividade"

    # Filter by project, show products
    if product not in (None, "Empty"):
        mask = mask & (filtered_df["Produto"] == product)
        groupby_field = "Atividade"

    # Group by project and sum hours
    filtered_df = filtered_df[mask]
    grouped = (
        filtered_df.groupby(groupby_field)["Horas totais"]
        .sum()
        .sort_values(ascending=False)
        .round(2)
    )

    # Create histogram
    hist_data = [
        go.Bar(
            x=[str(k) for k in grouped.index],
            y=grouped.values,
            text=[f"{round(v, 2)} h" for v in grouped.values],
            hovertemplate=[
                f"{round(v, 2)} h<br>{k}<extra></extra>"
                for k, v in zip(grouped.index, grouped.values)
            ],  # Full x-values in hovertemplate
            marker=dict(
                color="#198238",  # Color hex code
            ),
        )
    ]
   
    # Create figure
    figure = go.Figure(data=hist_data, layout=layout)

    return figure

# DropDownList - Colleague
@app.callback(
    Output("colleague-dropdown", "options"),
    [
        Input("colleague-dropdown", "value"),
    ]
)
def update_project_options(something):
    #if something is None:
    #    return [{'label': 'No selection', 'value': 'No selection'}]
    
    options = [{"label": i, "value": i} for i in extractor.data.keys()]
    options.sort(key=lambda x: x["label"])
    return options

# DropDownList - Projeto
@app.callback(
    Output("project-dropdown", "options"),
    [
        Input("colleague-dropdown", "value"),
    ],
)
def update_project_options(colleague):
    if colleague is None:
        return [{'label': 'No selection', 'value': 'No selection'}]
    
    project_project = extractor.product_project_list[colleague]
    project_no_na = project_project["Projeto"].dropna()
    project_unique = project_no_na.unique()
    options = [{"label": i, "value": i} for i in project_unique]
    options.sort(key=lambda x: x["label"])
    return options


# DropDownList - Produto
@app.callback(
    Output("product-dropdown", "options"),
    [Input("colleague-dropdown", "value"), Input("project-dropdown", "value")],
)
def update_product_options(colleague, project):
    if colleague is None:
        return [{'label': 'No selection', 'value': 'No selection'}]
    
    # Get project-product list
    product_project = extractor.product_project_list[colleague]

    if project is not None:
        mask = product_project["Projeto"] == project
        product_project = product_project[mask]

    product_no_na = product_project["Produto"].dropna()
    product_unique = product_no_na.unique()
    options = [{"label": i, "value": i} for i in product_unique]
    options.sort(key=lambda x: x["label"])
    return options
