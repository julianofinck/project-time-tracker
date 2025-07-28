from dotenv import load_dotenv

load_dotenv()

# These 'noqa' must be kept so that ruff does not complaing about it.
# Env vars must be loaded before anything else
from dash import ClientsideFunction, Dash, Input, Output  # noqa

from app.callbacks import register_callbacks  # noqa
from app.layout import generated_layout  # noqa
from app.state import load_app_state  # noqa
from app.utils.logger import set_logging_basic_config  # noqa

set_logging_basic_config(__file__)

# Load state
app_state = load_app_state()

# Create app
app = Dash(__name__)
app.title = "Apontamentos"
app.layout = generated_layout
server = app.server

register_callbacks(app, app_state)

# Client-side callback
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="reloadPage"),
    Output("page-location", "pathname"),
    Input("reload-flag", "data"),
)
