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
        Input("colleague-selector", "value"),
        Input("project-selector", "value"),
        Input("product-selector", "value"),
        Input("tabs-container", "value"),
    ],
)
def update_hist_commitment(
    start_date, end_date, colleague, project, product, tab_option
):
    df = app_state.data.valid

    # Get no valid register
    no_valid_register = [
        _coll for _coll in app_state.colleague_list if _coll not in list(df.colleague)
    ]

    # Remove former employees
    former_employees = os.getenv("FORMER_EMPLOYEES")
    former_employees = [
        e.strip() for e in former_employees.replace(" e ", ", ").split(",")
    ]
    df = df[~df["colleague"].isin(former_employees)].reset_index(drop=True)

    # Last reported day
    if tab_option == "last-reported-day":
        return last_reported_day(df, no_valid_register)

    # Boxplot
    if tab_option == "boxplot":
        return boxplot(df)

    # Elapsed/Reported
    if tab_option == "elapsed-reported":
        return reported_workhours(df)
