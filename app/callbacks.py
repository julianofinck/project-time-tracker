import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Input, Output, State, clientside_callback
from .__init__ import app
from .extract import extractor
import datetime
import threading
import time
import plotly

# Global progress variable
progress = 0
running_thread = False



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
        df = extractor._get_df(filename, colleague) 

        # Ignore those colleagues that barelly fill their working hours
        if len(df) >= 10:
            data[colleague] = df
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
        autosize=True,
        plot_bgcolor='lightgrey',
        margin=dict(
                l=14,
                r=14,
                b=14,
                t=14,
                pad=5
            ),
    )

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
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ]
)
def update_colleague_options(something, start_date, end_date):
    options = [{"label": i, "value": i} for i in extractor.data.keys()]
    options.sort(key=lambda x: x["label"])
    return options

# DropDownList - Projeto
@app.callback(
    Output("project-dropdown", "options"),
    [
        Input("colleague-dropdown", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
)
def update_project_options(colleague, start_date, end_date):
    if colleague is None:
        text = "Select a colleague"
        return [{'label': text, 'value': text}]
    
    # Filter by date
    data = extractor.data[colleague]
    mask = (data.Data > start_date) & (data.Data < end_date)
    projects = data[mask].Projeto.dropna().unique()
    projects.sort()
    options = [{"label": i, "value": i} for i in projects]
    options.sort(key=lambda x: x["label"])
    return options


# DropDownList - Produto
@app.callback(
    Output("product-dropdown", "options"),
    [
        Input("colleague-dropdown", "value"), 
        Input("project-dropdown", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
)
def update_product_options(colleague, project, start_date, end_date):
    if colleague is None:
        text = "Select a colleague"
        return [{'label': text, 'value': text}]
    
    # Filter by date
    data = extractor.data[colleague]
    mask = (data.Data > start_date) & (data.Data < end_date)
    data = data[mask]

    # Filter by project (Codex)
    if str(project).lower() == "codex":
        text = "Sem produto"
        return [{'label': text, 'value': text}]
    
    # Filter by project
    if project is not None:
        mask = data.Projeto == project
        data = data[mask]

    products = data.Produto.dropna().unique()
    products.sort()
    options = [{"label": i, "value": i} for i in products]
    options.sort(key=lambda x: x["label"])
    return options

# Commitment-Histogram
@app.callback(
    Output("histogram-commitment", "figure"),
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("colleague-dropdown", "value"),
        Input("project-dropdown", "value"),
        Input("product-dropdown", "value"),
    ],
)
def update_histogram(start_date, end_date, colleague, project, product):
    
    df = extractor._individual_commitment()

    # Adjust hasty employees
    today = datetime.datetime.now().date()
    hasty_df = df[df.last_date > today]
    tomorrow = today + datetime.timedelta(1)
    quantity = len(hasty_df)
    texto = [f"{row.indices[0]} ({row.last_date})" for _, row in hasty_df.iterrows()]
    texto = "Colegas do Futuro:<br>" + "<br>".join(texto)
    hasty_row = [tomorrow, texto, quantity]
    df.loc[len(df)] = hasty_row

    start_date = df['last_date'].min() - datetime.timedelta(1)
    end_date = tomorrow + datetime.timedelta(1)

    # Create layout for histogram
    layout = go.Layout(
        xaxis=dict(
            tickangle=-35,
            tickfont=dict(size=8),
            range=[start_date, end_date]),
            #paper_bgcolor='lightgrey',  # Background color of the entire paper
            plot_bgcolor='lightgrey',  # Background color of the plotting area
            margin=dict(
                l=14,
                r=14,
                b=14,
                t=14,
                pad=5
            ),
    )
    # TODO: Change the hardcoded "7" for something more responsive

    # Create histogram
    hist_data = [
        go.Bar(
            x=[str(k) for k in df.last_date],
            y=df.quantity,
            text=[f"{v}" for v in df.indices],
            hovertemplate=[
                f"{v} <br>{k}<extra></extra>"
                for k, v in zip(df.last_date, df.indices)
            ],  # Full x-values in hovertemplate
            marker=dict(
                color="#198238",  # Color hex code
            ),
        )
    ]
   
    # Create figure
    figure = go.Figure(data=hist_data, layout=layout)
    figure = go.Figure(data=hist_data, layout=layout)

    return figure
