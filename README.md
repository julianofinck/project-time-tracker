# Working Hours Dashboard
In short, this is a project and time tracking tool with data visualization. Our company keeps track of working hours in projects in four excel worksheets, which are filled in daily by colleagues. Each excel worksheet has a sheet named after the colleague responsible for filling it with the name of the project, product and task name. Each row also encompasses the time spent in it:
- [A_ao_F_APONTAMENTOS_OPE_2023](
https://imgoffice.sharepoint.com/:x:/r/sites/Codex-Operao/_layouts/15/Doc.aspx?sourcedoc=%7Bbf857d1f-05ab-453d-9472-60d8fe7fed22%7D)
- [G_ao_K_APONTAMENTOS_OPE_2023](
https://imgoffice.sharepoint.com/:x:/r/sites/Codex-Operao/_layouts/15/doc2.aspx?sourcedoc=%7BEB37A5BB-D897-4ECC-9F55-FC07BDC22CF0%7D&file=G_ao_K_APONTAMENTOS_OPE_2023.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1)
- [L_ao_P_APONTAMENTOS_OPE_2023](
https://imgoffice.sharepoint.com/:x:/r/sites/Codex-Operao/_layouts/15/Doc.aspx?sourcedoc=%7B4806d9fc-966a-4372-b117-b9d92d266ca6%7D)
- [R_ao_Z_APONTAMENTOS_OPE_2023](
https://imgoffice.sharepoint.com/:x:/r/sites/Codex-Operao/_layouts/15/Doc.aspx?sourcedoc=%7B45261a51-ac24-4499-b8e7-813730aaccbc%7D)

||||
|---|---|---|
|💪 |Core tech|[![Python 3.8](https://img.shields.io/badge/Python-3.8-3776AB?style=flat&logo=python&logoColor=white)](https://docs.python.org/3.8/) [![Dash 2.0.0](https://img.shields.io/badge/Dash-2.0.0-00CCBB?style=flat&logo=dash&logoColor=white)](https://dash.plotly.com/) [![Flask 2.0.1](https://img.shields.io/badge/Flask-2.0.1-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/en/2.0.1/) [![Pandas 1.3.3](https://img.shields.io/badge/Pandas-1.3.3-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
|😎 | Style | [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)|

## How to install
```shell
# Create a virtual environment
python3 -m venv .venv      # Linux

# Activate it
source .venv/bin/activate  # Linux

# Install requirements using "pip"
pip install -r requirements.txt
```
run it with `python run.py`

## To Do:
- Rank colleagues by percentage of days filled since start, number of days filled in, number of workdays since start, 1st day, last filled in day
- Get participants in a specific product and in a project
