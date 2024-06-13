import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Input, Output
from .__init__ import app
from .extract import extractor
import datetime


# Button
@app.callback(
    Output("update-button", "children"), 
    [Input("update-button", "n_clicks")]
)
def update_button(n_clicks):
    if n_clicks is not None:
        print("I was clicked")
        extractor.update_data()
    return "Ler planilhas"

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
        return tuple(["01/01/0101"] * 4)
    
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
