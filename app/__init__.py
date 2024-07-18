import os
import pickle

from dash import Dash

from .import_data import DataImporter
from .layout import Layout


# Load the extractor if it exists in cache
if os.path.exists("app/cache/state.pickle"):
    with open("app/cache/state.pickle", "rb") as f:
        data_importer = pickle.load(f)

        # For integration purposes
        data_importer.data.to_pickle("app/cache/valid_data.pickle")
else:
    data_importer = DataImporter()
    data_importer.get_dfs()
    data_importer.save_state()


# Create app
app = Dash(__name__)
app.title = "Codex Apontamentos"

# Define layout
app.layout = Layout().generate()

# Add callbacks
from .callbacks import *
