import os

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, Input, Output, clientside_callback, dcc, html
from dotenv import load_dotenv

from .get_data import Extractor
from .layout import DropDownLists, Layout

load_dotenv()

path = os.getenv("HOURS_XLSX")
extractor = Extractor(path)
# colleagues_list = extractor.get_colleagues()
colleagues_list = ["Juliano", "Klever", "José"]
dfs = extractor.get_dfs(colleagues_list)

drop_down_lists = DropDownLists(dfs)

# Create app
app = Dash(__name__)

# Define layout
app.layout = Layout(drop_down_lists).layout()


## ---- Define callbacks ----
# DatePickerRange
@app.callback(
    Output("date-picker", "min_date_allowed"),
    Output("date-picker", "max_date_allowed"),
    Output("date-picker", "start_date"),
    Output("date-picker", "end_date"),
    [Input("colleague-dropdown", "value")],
)
def update_date_picker(colleague):
    df = dfs[colleague]
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
    # Get the data accordingly
    df = dfs[colleague]

    # Filter data based on selected dates
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
    filtered_df = df[(df["Data"] >= start_datetime) & (df["Data"] <= end_datetime)]

    # Filter by project, show products
    groupby_field = "Projeto"
    mask = [True] * len(filtered_df)
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
            x=[str(k)[:14] for k in grouped.index],
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

    # Create layout for histogram
    layout = go.Layout(
        xaxis=dict(tickangle=-35, tickfont=dict(size=8)),
        autosize=False,
        height=200,
        margin=dict(l=7, r=7, b=7, t=7, pad=0),
    )
    # TODO: Change the hardcoded "7" for something more responsive

    # Get browser view width and height

    # Create figure
    figure = go.Figure(data=hist_data, layout=layout)

    return figure


# DropDownList - Projeto
@app.callback(
    Output("project-dropdown", "options"),
    [
        Input("colleague-dropdown", "value"),
    ],
)
def update_project_options(colleague):
    project_project = drop_down_lists.product_project_list[colleague]
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
    # Get project-product list
    product_project = drop_down_lists.product_project_list[colleague]

    if project is not None:
        mask = product_project["Projeto"] == project
        product_project = product_project[mask]

    product_no_na = product_project["Produto"].dropna()
    product_unique = product_no_na.unique()
    options = [{"label": i, "value": i} for i in product_unique]
    options.sort(key=lambda x: x["label"])
    return options


if __name__ == "__main__":
    app.run_server(debug=True)
