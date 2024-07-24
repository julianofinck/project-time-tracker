import datetime

from dash import Input, Output

from app import app, app_state
from app.translate.translator import translator


## Header Dropdown Lists #######################################################################
# DateRange
@app.callback(
    Output("date-picker", "min_date_allowed"),
    Output("date-picker", "max_date_allowed"),
    Output("date-picker", "start_date"),
    Output("date-picker", "end_date"),
    [Input("employee-selector", "value")],
)
def update_date_picker(employee):
    data = app_state.data.valid.copy()

    if employee is None:
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
        data = data[data["employee"] == employee]
        return (
            data["date"].min().strftime("%Y-%m-%d"),
            data["date"].max().strftime("%Y-%m-%d"),
            data["date"].min().strftime("%Y-%m-%d"),
            data["date"].max().strftime("%Y-%m-%d"),
        )


# employee
@app.callback(
    Output("employee-selector", "options"),
    [
        Input("employee-selector", "value"),
        Input("project-selector", "value"),
        Input("product-selector", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
)
def update_employee_options(employee, project, product, start_date, end_date):
    # if employee is not None:
    #    return [{"label": i, "value": i} for i in [employee]]

    # Filter date initial mask
    data = app_state.data.valid
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    mask = (data["date"] >= start_date) & (data["date"] <= end_date)

    if project is not None:
        mask = mask & (data["project"] == project)
    if product is not None:
        if project == "CODEX":
            activity = product
            mask = mask & (data["activity"] == activity)
        else:
            mask = mask & (data["product"] == product)

    options = [{"label": i, "value": i} for i in data[mask]["employee"].unique()]
    options.sort(key=lambda x: x["label"])
    return options


# Project
@app.callback(
    Output("project-selector", "options"),
    [
        Input("employee-selector", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
)
def update_project_options(employee, start_date, end_date):
    # Filter date initial mask
    data = app_state.data.valid
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    mask = (data["date"] >= start_date) & (data["date"] <= end_date)

    if employee is None:
        projects = data[mask]["project"].dropna().unique()
    else:
        projects = data[mask & (data["employee"] == employee)].project.dropna().unique()

    projects.sort()
    return [{"label": project, "value": project} for project in projects]


# Product
@app.callback(
    Output("product-selector", "options"),
    Output("product-selector-title", "children"),
    [
        Input("employee-selector", "value"),
        Input("project-selector", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
)
def update_product_options(employee, project, start_date, end_date):
    # Filter date initial mask
    data = app_state.data.valid
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    mask = (data["date"] >= start_date) & (data["date"] <= end_date)

    if employee is None and project is None:
        products = data[mask]["product"].dropna().unique()

    elif employee is None and project is not None:
        if project == "CODEX":
            # todo: add javascript that changes label "Produto" to "Atividade" if CODEX is picked
            products = (
                data[mask & (data["project"] == project)]["activity"].dropna().unique()
            )
        else:
            products = (
                data[mask & (data["project"] == project)]["product"].dropna().unique()
            )

    elif employee is not None and project is None:
        products = (
            data[mask & (data["employee"] == employee)]["product"].dropna().unique()
        )

    elif employee is not None and project is not None:
        if project == "CODEX":
            # todo: add javascript that changes label "Produto" to "Atividade" if CODEX is picked
            products = (
                data[
                    mask & (data["employee"] == employee) & (data["project"] == project)
                ]["activity"]
                .dropna()
                .unique()
            )
        else:
            products = (
                data[
                    mask & (data["employee"] == employee) & (data["project"] == project)
                ]["product"]
                .dropna()
                .unique()
            )

    products.sort()
    options = [{"label": product, "value": product} for product in products]

    # CODEX has no produtos.
    if project == "CODEX":
        return options, translator.translate("Activity")
    else:
        return options, translator.translate("Product")
