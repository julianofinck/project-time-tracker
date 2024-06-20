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

    # Concatenate
    data = pd.concat(data.values()).reset_index(drop=True)

    # Adjust column names
    data.columns = ["date", "project", "product", "activity", "hours", "colleague"]

    # Store in class
    extractor.data = data

    # Print elapsed time
    tf = time.time()
    print("Elapsed time:", int(tf - ti), "s")

    # Save state
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
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(7)).strftime("%Y-%m-%d")
        today = today.strftime("%Y-%m-%d")
        
        return (
            yesterday,
            today,
            yesterday,
            today
        )
    
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

    # TODO: Case in which data is empty

    # Filter date initial mask
    data = extractor.data
    mask = (start_date <data["date"]) & (data.date < end_date)

    # Neither project nor product selected -> show project
    if project is None and product is None:
        if colleague is not None:
            mask = mask & (data["colleague"] == colleague)
        grouped = data.loc[mask, ["project", "hours"]].groupby(["project"]).sum()
    
    # Project selected, Product is none
    elif project is not None and product is None:
        mask = mask & (data["project"] == project)
        if colleague is not None:
            mask = mask & (data["colleague"] == colleague)

        # CODEX case
        if project == "CODEX":
            grouped = data.loc[mask, ["activity", "hours"]].groupby(["activity"]).sum()
        else:
            grouped = data.loc[mask, ["product", "hours"]].groupby(["product"]).sum()
    
    # Project is none, Product selected
    elif project is None and product is not None:
        mask = mask & (data["product"] == product)
        if colleague is not None:
            mask = mask & (data["colleague"] == colleague)
        grouped = data.loc[mask, ["activity", "hours"]].groupby(["activity"]).sum()

    # Project selected, Product selected
    elif project is not None and product is not None:
        mask = mask & (data["project"] == project) & (data["product"] == product)
        if colleague is not None:
            mask = mask & (data["colleague"] == colleague)

        # CODEX case
        if project == "CODEX":
            grouped = data.loc[mask, ["activity", "hours"]].groupby(["activity"]).sum()
        else:
            grouped = data.loc[mask, ["activity", "hours"]].groupby(["activity"]).sum()
    
    # Sort values and make hist_data
    grouped = grouped.sort_values(by="hours", ascending=False)
    hist_data = [
        go.Bar(
            x=[x for x in grouped.index],
            y=[h for h in grouped.hours],
            text=[f"{round(v, 2)} h" for v in grouped.hours],
            hovertemplate=[
                f"{round(h, 2)} h<br>{x}<extra></extra>"
                for x, h in zip(grouped.index, grouped.hours)
            ],
            marker=dict(
                color="#198238",  # Color hex code
            ),
        )
    ]

    # Create figure
    figure = go.Figure(data=hist_data)
    return figure


# DropDownList - Colleague
@app.callback(
    Output("colleague-dropdown", "options"),
    [
        Input("colleague-dropdown", "value"),
        Input("project-dropdown", "value"),
        Input("product-dropdown", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ]
)
def update_colleague_options(colleague, project, product, start_date, end_date):
    # Filter date initial mask
    data = extractor.data
    mask = (start_date <data["date"]) & (data.date < end_date)

    if project is not None:
        mask = mask & (data["project"] == project)
    if product is not None:
        mask = mask & (data["product"] == product)

    options = [{"label": i, "value": i} for i in data[mask]["colleague"].unique()]
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
    data = extractor.data
    filter_date = (start_date <data["date"]) & (data.date < end_date)
    
    if colleague is None:
        projects = data[filter_date]["project"].dropna().unique()
        projects.sort()
        return [{'label': project, 'value': project} for project in projects]
    else:
        projects = data[filter_date & (data["colleague"] == colleague)].project.dropna().unique()
        projects.sort()
        return [{'label': project, 'value': project} for project in projects]


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
    data = extractor.data
    filter_date = (start_date <data["date"]) & (data.date < end_date)

    if colleague is None and project is None:
        products = data[filter_date]["product"].dropna().unique()
        
    elif colleague is None and project is not None:
        if project == "CODEX":
            # todo: add javascript that changes label "Produto" to "Atividade" if CODEX is picked
            products = data[filter_date & (data["project"] == project)]["activity"].dropna().unique()
        else:
            products = data[filter_date & (data["project"] == project)]["product"].dropna().unique()
        
    elif colleague is not None and project is None:
        products = data[filter_date & (data["colleague"] == colleague)]["product"].dropna().unique()
    
    elif colleague is not None and project is not None:
        if project == "CODEX":
            # todo: add javascript that changes label "Produto" to "Atividade" if CODEX is picked
            products = data[filter_date & (data["colleague"] == colleague) & (data["project"] == project)]["activity"].dropna().unique()
        else:
            products = data[filter_date & (data["colleague"] == colleague) & (data["project"] == project)]["product"].dropna().unique()
        

    products.sort()
    options = [{'label': product, 'value': product} for product in products]
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

    data = extractor.data
    
    # Get date of last filled day and groupby day
    df = data[["colleague", "date"]].groupby(by="colleague", as_index=False).max()
    df = df.groupby("date", as_index=False)["colleague"].apply(', '.join)
    df["date"] = df["date"].apply(lambda date: date.date())

    # Count quantity
    df["quantity"] = df["colleague"].apply(lambda x: x.count(",") + 1)

    # Adjust hasty employees
    today = datetime.datetime.now().date()
    tomorrow = (today + datetime.timedelta(1))
    hasty_mask = df["date"] > today
    hasty_df = df[hasty_mask]
    quantity = hasty_df["quantity"].sum()

    texto = [f"{row['colleague']} ({row['date'].strftime('%Y-%m-%d')})" for _, row in hasty_df.iterrows()]
    texto = "Colegas do Futuro:<br>" + "<br>".join(texto)

    # Eliminate future dates
    # TODO:

    # Add new register for visualizaiton
    df.loc[len(df)] = [tomorrow, texto, quantity]

    # Count
    df.groupby("date").size().reset_index(name="quantity")

    start_date = df["date"].min() - datetime.timedelta(1)
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
            x=df["date"],
            y=df["quantity"],
            text=df["colleague"],
            hovertemplate=[
                f"{v} <br>{k}<extra></extra>"
                for k, v in zip(df["date"], df["colleague"])
            ],  # Full x-values in hovertemplate
            marker=dict(
                color="#198238",  # Color hex code
            ),
        )
    ]
   
    # Create figure
    figure = go.Figure(data=hist_data, layout=layout)

    return figure
