import os

import plotly.graph_objs as go
from dash import Input, Output

from app import app, app_state
from app.commitment_card_processor import (boxplot, last_reported_day,
                                           reported_workhours)


# Commitment-Histogram
@app.callback(
    Output("histogram-commitment", "figure"),
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("employee-selector", "value"),
        Input("project-selector", "value"),
        Input("product-selector", "value"),
        Input("tabs-container", "value"),
    ],
)
def update_hist_commitment(
    start_date, end_date, employee, project, product, tab_option
):
    data = app_state.data

    # Get employees with only invalid registers
    eir = [
        employee 
        for employee in app_state.employee_list
        if employee not in list(data.valid.employee.unique())
    ]

    # Remove former employees
    df = data.valid
    former_employees = os.getenv("FORMER_EMPLOYEES")
    former_employees = [
        e.strip() 
        for e in former_employees.replace(" e ", ", ").split(",")
    ]
    df = df[~df["employee"].isin(former_employees)].reset_index(drop=True)

    # Last reported day
    if tab_option == "last-reported-day":
        return last_reported_day(df, eir)

    # Boxplot
    if tab_option == "boxplot":
        return boxplot(df)

    # Elapsed/Reported
    if tab_option == "elapsed-reported":
        return reported_workhours(df)
