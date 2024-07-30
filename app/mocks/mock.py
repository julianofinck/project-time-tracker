import pandas as pd


def mock_state(app_state):
    # Mock employee list
    mock_employee = {
        employee: f"John{i:0>3}" for i, employee in enumerate(app_state.employee_list)
    }
    app_state.employee_list = list(mock_employee.values())

    # Mock data
    app_state.data.valid = mock_data(app_state.data.valid, mock_employee)
    app_state.data.invalid = mock_data(app_state.data.invalid, mock_employee)

    # xlsx
    mock_paths = {
        path: f"path/to/file{i:0>3}" for i, path in enumerate(app_state.xlsx.values())
    }
    app_state.xlsx = {k: mock_paths[path] for k, path in app_state.xlsx.items()}

    # Filename employees
    app_state.filename_employees = {
        mock_paths[path]: [mock_employee[employee] for employee in employees]
        for path, employees in app_state.filename_employees.items()
    }

    return app_state


def mock_data(data, mock_employee):
    # unique projects
    projects = {
        project: f"Project{i:0>3}"
        for i, project in enumerate(data["project"].unique())
        if not pd.isna(project)
    }

    # unique products
    products = {
        product: f"Product{i:0>3}"
        for i, product in enumerate(data["product"].unique())
        if not pd.isna(product)
    }

    # unique activities
    activities = {
        activity: f"Activity{i:0>4}"
        for i, activity in enumerate(data["activity"].unique())
        if not pd.isna(activity)
    }
    return data.replace({**projects, **products, **activities, **mock_employee})
