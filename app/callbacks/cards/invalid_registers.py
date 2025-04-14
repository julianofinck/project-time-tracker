import datetime

import pandas as pd
from dash import Input, Output

from app import app, app_state
from app.languages.translator import translator


# Controller - Invalid Registers
@app.callback(
    Output("controller-table", "rowData"),
    Output("controller-table", "columnDefs"),
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("employee-selector", "value"),
        Input("project-selector", "value"),
        Input("product-selector", "value"),
    ],
)
def update_hist_invalid_registers(start_date, end_date, employee, project, product):
    df = app_state.data.invalid.copy()

    columns = ["employee", "line", "date", "hours", "project", "product", "activity"]

    # Filter by employee
    if employee:
        if employee in df["employee"].unique():
            df = df[df["employee"] == employee]
        else:
            columns = [translator.translate(c).capitalize() for c in columns]
            columns = [{"name": i, "id": i} for i in columns]
            return None, columns

    # Sort by date and start time
    df = df.sort_values(
        by=["employee", "date", "start_time"], ascending=[True, False, False]
    ).copy()

    # Adjust columns order
    df = df[columns]


    # Adjust date
    df["date"] = df["date"].apply(
        lambda x: x.date() if isinstance(x, datetime.datetime) else x
    )
    df["date"] = df["date"].apply(lambda x: str(x) if pd.isna(x) else str(x))

    # Get columns
    df.columns = [translator.translate(c).capitalize() for c in df.columns]
    columns = [{"field": c} for c in df.columns]

    # Get data
    data = df.to_dict("records")

    return data, columns
