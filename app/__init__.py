import os
import pickle
import logging

from dash import Dash

from app.app_state import AppState
import app.utils.logger as logger




#def initialize_app() -> Dash:
# Start logger
logger.start_it()

try:
    # Load from cache disk
    with open("app/cache/state.pickle", "rb") as f:
        app_state = pickle.load(f)

        # For integration purposes
        app_state.data.valid.to_pickle("app/cache/valid_data.pickle")
except FileNotFoundError:
    # Create it
    app_state = AppState()
    app_state.get_dfs()
    app_state.save_state()

# Check if mock
if str(os.getenv("MOCK_DATA")).lower() == "true":
    from app.mocks.mock import mock_state

    app_state = mock_state(app_state)
    logger.warning("Mocked data!")


# Create app
app = Dash(__name__)
app.title = "Apontamentos"
server = app.server

# Define layout
from app.layout import generated_layout

app.layout = generated_layout

# Add callbacks

from dash import ClientsideFunction

from app.callbacks import *
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="reloadPage"),
    Output("page-location", "pathname"),
    Input("reload-flag", "data")
)
