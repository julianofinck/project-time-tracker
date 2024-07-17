import datetime
import os

import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State

from . import app
from .__init__ import data_importer
from .callback_update import *
from .boxplot import boxplot
from .reported_workhours import reported_workhours


## Header Dropdown Lists #######################################################################
# Colleague
@app.callback(
    Output("colleague-selector", "options"),
    [
        Input("colleague-selector", "value"),
        Input("project-selector", "value"),
        Input("product-selector", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
)
def update_colleague_options(colleague, project, product, start_date, end_date):
    # Filter date initial mask
    data = data_importer.data
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    mask = (data["date"] >= start_date) & (data["date"] <= end_date)

    if project is not None:
        mask = mask & (data["project"] == project)
    if product is not None:
        mask = mask & (data["product"] == product)

    options = [{"label": i, "value": i} for i in data[mask]["colleague"].unique()]
    options.sort(key=lambda x: x["label"])
    return options


# Project
@app.callback(
    Output("project-selector", "options"),
    [
        Input("colleague-selector", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
)
def update_project_options(colleague, start_date, end_date):
    # Filter date initial mask
    data = data_importer.data
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    mask = (data["date"] >= start_date) & (data["date"] <= end_date)

    if colleague is None:
        projects = data[mask]["project"].dropna().unique()
    else:
        projects = (
            data[mask & (data["colleague"] == colleague)].project.dropna().unique()
        )

    projects.sort()
    return [{"label": project, "value": project} for project in projects]


# Product
@app.callback(
    Output("product-selector", "options"),
    Output("product-selector-title", "children"),
    [
        Input("colleague-selector", "value"),
        Input("project-selector", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
)
def update_product_options(colleague, project, start_date, end_date):
    # Filter date initial mask
    data = data_importer.data
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    mask = (data["date"] >= start_date) & (data["date"] <= end_date)

    if colleague is None and project is None:
        products = data[mask]["product"].dropna().unique()

    elif colleague is None and project is not None:
        if project == "CODEX":
            # todo: add javascript that changes label "Produto" to "Atividade" if CODEX is picked
            products = (
                data[mask & (data["project"] == project)]["activity"].dropna().unique()
            )
        else:
            products = (
                data[mask & (data["project"] == project)]["product"].dropna().unique()
            )

    elif colleague is not None and project is None:
        products = (
            data[mask & (data["colleague"] == colleague)]["product"].dropna().unique()
        )

    elif colleague is not None and project is not None:
        if project == "CODEX":
            # todo: add javascript that changes label "Produto" to "Atividade" if CODEX is picked
            products = (
                data[
                    mask
                    & (data["colleague"] == colleague)
                    & (data["project"] == project)
                ]["activity"]
                .dropna()
                .unique()
            )
        else:
            products = (
                data[
                    mask
                    & (data["colleague"] == colleague)
                    & (data["project"] == project)
                ]["product"]
                .dropna()
                .unique()
            )

    products.sort()
    options = [{"label": product, "value": product} for product in products]

    # CODEX has no produtos.
    if project == "CODEX":
        return options, "Atividade"
    else:
        return options, "Produto"

#########################################################################################
# Main Histogram
@app.callback(
    Output("histogram", "figure"),
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("colleague-selector", "value"),
        Input("project-selector", "value"),
        Input("product-selector", "value"),
    ],
)
def update_hist_workhours(start_date, end_date, colleague, project, product):
    # TODO: Case in which data is empty

    # Filter date initial mask
    data = data_importer.data
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    mask = (data["date"] >= start_date) & (data["date"] <= end_date)

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
        if colleague is not None:
            mask = mask & (data["colleague"] == colleague)

        # CODEX case
        if project == "CODEX":
            mask = mask & (data["project"] == project) & (data["activity"] == product)
            grouped = (
                data.loc[mask, ["colleague", "hours"]].groupby(["colleague"]).sum()
            )
        else:
            mask = mask & (data["project"] == project) & (data["product"] == product)
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

    # Create layout for histogram
    layout = go.Layout(
        xaxis=dict(tickangle=-35, tickfont=dict(size=8)),
        autosize=True,
        plot_bgcolor="lightgrey",
        margin=dict(l=14, r=14, b=14, t=14, pad=5),
    )

    # Create figure
    figure = go.Figure(data=hist_data, layout=layout)
    return figure


# DatePickerRange
@app.callback(
    Output("date-picker", "min_date_allowed"),
    Output("date-picker", "max_date_allowed"),
    Output("date-picker", "start_date"),
    Output("date-picker", "end_date"),
    [Input("colleague-selector", "value")],
)
def update_date_picker(colleague):
    data = data_importer.data.copy()

    if colleague is None:
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(365)).strftime("%Y-%m-%d")
        today = today.strftime("%Y-%m-%d")

        return (
            data["date"].min().strftime("%Y-%m-%d"),
            data["date"].max().strftime("%Y-%m-%d"),
            yesterday,
            today,
        )
    else:
        data = data[data["colleague"] == colleague]
        return (
            data["date"].min().strftime("%Y-%m-%d"),
            data["date"].max().strftime("%Y-%m-%d"),
            data["date"].min().strftime("%Y-%m-%d"),
            data["date"].max().strftime("%Y-%m-%d"),
        )


# Controller - Invalid Registers
@app.callback(
    Output("controller-table", "data"),
    Output("controller-table", "columns"),
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("colleague-selector", "value"),
        Input("project-selector", "value"),
        Input("product-selector", "value"),
    ],
)
def update_hist_invalid_registers(start_date, end_date, colleague, project, product):
    invalid = data_importer.invalid.copy()

    # Filter by colleague
    if colleague in invalid["colleague"].unique():
        invalid = invalid[invalid["colleague"] == colleague]

    # Adjust column order for controller
    invalid = invalid[
        ["colleague", "index", "date", "hours", "project", "product", "activity"]
    ]

    # Adjust date
    invalid["date"] = invalid["date"].apply(
        lambda x: x.date() if isinstance(x, datetime.datetime) else x
    )
    invalid["date"].apply(lambda x: str(x) if pd.isna(x) else str(x))

    # Adjust columns to portuguese
    invalid.columns = [
        "Colaborador",
        "Linha",
        "Data",
        "Horas",
        "Projeto",
        "Produto",
        "Atividade",
    ]
    columns = [{"name": i, "id": i} for i in invalid.columns]
    return invalid.to_dict("records"), columns


# Commitment-Histogram
@app.callback(
    Output("histogram-commitment", "figure"),
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("colleague-selector", "value"),
        Input("project-selector", "value"),
        Input("product-selector", "value"),
        Input("tabs-container", "value"),
    ],
)
def update_hist_commitment(start_date, end_date, colleague, project, product, tab_option):
    data = data_importer.data

    # Boxplot
    if tab_option=="value2":
        return boxplot(data)
    
    # FilledDays/Workdays
    if tab_option=="value3":
        return reported_workhours(data)
        pass

    # Get date of last filled day and groupby day
    df = data[["colleague", "date"]].groupby(by="colleague", as_index=False).max()

    # Get no valid register
    no_valid_register = [_coll for _coll in data_importer.colleague_list if _coll not in list(df.colleague)]

    # Remove former employees
    former_employees = os.getenv("FORMER_EMPLOYEES")
    former_employees = [
        e.strip() for e in former_employees.replace(" e ", ", ").split(",")
    ]
    df = df[~df["colleague"].isin(former_employees)].reset_index(drop=True)

    # Group by date
    df = df.groupby("date", as_index=False)["colleague"].apply(", ".join)

    # Count quantity
    df["quantity"] = df["colleague"].apply(lambda x: x.count(",") + 1)

    # Add colleague who never filled the table properly as well
    if no_valid_register:
        no_valid_register.sort()
        min_date = df["date"].min() - datetime.timedelta(1)
        texto = "Sem registro válido:<br>" + ", ".join(no_valid_register)
        df.iloc[-1] = [min_date, texto, len(no_valid_register)]

    # Adjust hasty employees
    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(1)
    hasty_mask = df["date"] > today
    hasty_df = df[hasty_mask]
    if not hasty_df.empty:
        quantity = hasty_df["quantity"].sum()
        texto = [
            f"{row['colleague']} ({row['date'].strftime('%Y-%m-%d')})"
            for _, row in hasty_df.iterrows()
        ]
        texto = "Colegas do Futuro:<br>" + "<br>".join(texto)

        # Remove hasty
        df = df[~hasty_mask].reset_index(drop=True)

        # Add new register for visualizaiton
        df.loc[len(df)] = [tomorrow, texto, quantity]

        # Count
        df.groupby("date").size().reset_index(name="quantity")
        
    # Order dataframe by date
    df = df.sort_values(by="date").reset_index(drop=True)

    # Graph settings
    start_date = df["date"].min() - datetime.timedelta(1)
    end_date = tomorrow + datetime.timedelta(1)

    # Create layout for histogram
    layout = go.Layout(
        xaxis=dict(tickangle=-35, tickfont=dict(size=8), range=[start_date, end_date]),
        # paper_bgcolor='lightgrey',  # Background color of the entire paper
        plot_bgcolor="lightgrey",  # Background color of the plotting area
        margin=dict(l=14, r=14, b=14, t=14, pad=5),
    )
    # TODO: Change the hardcoded "7" for something more responsive

    # Get colors
    colors = ["#198238"] * len(df)
    if no_valid_register:
        colors[0] = "red"
    if not hasty_df.empty:
        colors[-1] = "#A47300"

    # Create histogram
    hist_data = [
        go.Bar(
            x=df["date"],
            y=df["quantity"],
            text=df["quantity"],
            hovertemplate=[
                f"{v} <br>{k}<extra></extra>"
                for k, v in zip(df["date"], df["colleague"])
            ],  # Full x-values in hovertemplate
            marker=dict(
                color=colors,  # Color hex code
            ),
        )
    ]

    # Create figure
    figure = go.Figure(data=hist_data, layout=layout)

    return figure
