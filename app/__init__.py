from dash import Dash

# Create app
app = Dash(__name__)

from .layout import Layout
from .callbacks import *

# Define layout
app.layout = Layout().generate()
