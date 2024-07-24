import datetime
import os

import pandas as pd
from dash import Input, Output

from app import app, app_state
from app.translate.translator import translator


# Controller - Invalid Registers
@app.callback(
    Output("controller-table", "data"),
    Output("controller-table", "columns"),
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("employee-selector", "value"),
        Input("project-selector", "value"),
        Input("product-selector", "value"),
    ],
)
def update_hist_invalid_registers(start_date, end_date, employee, project, product):
    invalid = app_state.data.invalid.copy()

    # Filter by employee
    if employee in invalid["employee"].unique():
        invalid = invalid[invalid["employee"] == employee]

    # Adjust column order for controller
    invalid = invalid[
        ["employee", "line", "date", "hours", "project", "product", "activity"]
    ]

    # Adjust date
    invalid["date"] = invalid["date"].apply(
        lambda x: x.date() if isinstance(x, datetime.datetime) else x
    )
    invalid["date"].apply(lambda x: str(x) if pd.isna(x) else str(x))

    # Adjust column names
    invalid.columns = [translator.translate(c).capitalize() for c in invalid.columns]
    columns = [{"name": i, "id": i} for i in invalid.columns]
    return invalid.to_dict("records"), columns
