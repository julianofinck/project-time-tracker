# Working Hours Dashboard
This project generates dynamic analytical graphs for enterprise management using Python's Dash library. It requires Excels worksheets to be available locally. They must have the following columns.

|employee|date|project|product|task|total hours|
|---|---|---|---|---|---|
|John|23/07/24|project1|product1.1|backend development|7.4

> Names inside the repository might be in Portuguese because I developed in a way to be easily plugable to Codex workhours worksheets back in the day.

## How to install
### Set the directory of the worksheets
The company's workhours worksheets must be locally available, as by using OneDrive-Desktop to add their **cloud directory** as a shortcut at your local. Copy the local path to this mirrored local directory and paste it as the environment variable `COMPANY_WORKHOURS_EXCELS_DIR` in the `.env`.

### Install project using [Poetry](https://python-poetry.org/docs/)
```shell
# Change directory into project directory
cd <project-dir>

# Install venv
poetry install

# Activate venv
poetry shell

# Run project
python run.py
```

## How it works?
Strong dependency on OneDrive shortcut.  
<div style="display: flex; justify-content: center; align-items: center; height: fit-content;">
    <img src="img/flowchart.svg" alt="Flowchart" style="background-color: white; height: 200px">
</div>
