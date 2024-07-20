import datetime
import os

import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State

from app import app, app_state
from app.commitment_card_processor import boxplot, reported_workhours
from app.translate.translator import translator

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
    invalid = app_state.data.invalid.copy()

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

    # Adjust column names
    columns =[
        "Employee",
        "Line",
        "Date",
        "Hours",
        "Project",
        "Product",
        "Activity",
    ]
    invalid.columns = [translator.translate(c) for c in columns]
    columns = [{"name": i, "id": i} for i in invalid.columns]
    return invalid.to_dict("records"), columns
