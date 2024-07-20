import os
import pickle

from dash import Dash

from .app_state import AppState
from .layout import Layout

# Load the extractor if it exists in cache
if os.path.exists("app/cache/state.pickle"):
    with open("app/cache/state.pickle", "rb") as f:
        app_state = pickle.load(f)

        # For integration purposes
        app_state.data.valid.to_pickle("app/cache/valid_data.pickle")
else:
    app_state = AppState()
    app_state.get_dfs()
    app_state.save_state()


# Create app
app = Dash(__name__)
app.title = "Codex Apontamentos"

# Define layout
from app.layout import generated_layout

app.layout = generated_layout

# Add callbacks
from app.callbacks import *
