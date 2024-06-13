from dash import Dash

# Create app
app = Dash(__name__)

from .layout import Layout


# Define layout
app.layout = Layout().generate()

from .callbacks import *
