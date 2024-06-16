from dash import Dash

# Create app
app = Dash(__name__)
app.title = "Codex Apontamentos"


from .layout import Layout
from .callbacks import *

# Define layout
app.layout = Layout().generate()
