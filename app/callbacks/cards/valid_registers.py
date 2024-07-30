import datetime

import plotly.graph_objs as go
from dash import Input, Output

from app import app, app_state
from app.languages.translator import translator


@app.callback(
    Output("histogram", "figure"),
    Output("valid-table", "columns"),
    Output("valid-table", "data"),
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("employee-selector", "value"),
        Input("project-selector", "value"),
        Input("product-selector", "value"),
    ],
)
def update_hist_workhours(start_date, end_date, employee, project, product):
    # TODO: Case in which data is empty

    # Filter date initial mask
    data = app_state.data.valid
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    mask = (data["date"] >= start_date) & (data["date"] <= end_date)

    # Neither project nor product selected -> show project
    if project is None and product is None:
        if employee is not None:
            mask = mask & (data["employee"] == employee)
        grouped = data.loc[mask, ["project", "hours"]].groupby(["project"]).sum()

    # Project selected, Product is none
    elif project is not None and product is None:
        mask = mask & (data["project"] == project)
        if employee is not None:
            mask = mask & (data["employee"] == employee)

        # CODEX case
        if project == "CODEX":
            grouped = data.loc[mask, ["activity", "hours"]].groupby(["activity"]).sum()
        else:
            grouped = data.loc[mask, ["product", "hours"]].groupby(["product"]).sum()

    # Project is none, Product selected
    elif project is None and product is not None:
        mask = mask & (data["product"] == product)
        if employee is not None:
            mask = mask & (data["employee"] == employee)
        grouped = data.loc[mask, ["activity", "hours"]].groupby(["activity"]).sum()

    # Project selected, Product selected
    elif project is not None and product is not None:
        if employee is not None:
            mask = mask & (data["employee"] == employee)

        # CODEX case
        if project == "CODEX":
            activity = product
            mask = mask & (data["project"] == project) & (data["activity"] == activity)
            grouped = data.loc[mask, ["activity", "hours"]].groupby(["activity"]).sum()
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
    fig = go.Figure(data=hist_data, layout=layout)

    # Get columns and data to dash_table
    dash_data, dash_columns = get_table(data[mask])

    return fig, dash_columns, dash_data


def get_table(df):
    # Sort by date and start time
    df = df.sort_values(
        by=["employee", "date", "start_time"], ascending=[True, False, False]
    ).copy()

    # Adjust columns order
    df = df[["employee", "line", "date", "project", "product", "activity", "hours"]]

    # Adjust date
    df["date"] = df["date"].apply(lambda x: x.strftime("%d/%m/%Y"))

    # Get columns
    df.columns = [translator.translate(c).capitalize() for c in df.columns]
    columns = [{"name": i, "id": i} for i in df.columns]

    # Get data
    data = df.to_dict("records")

    return data, columns
