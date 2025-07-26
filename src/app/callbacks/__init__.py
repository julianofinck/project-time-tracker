from .cards import register_cards_callbacks
from .headers import register_headers_callbacks
from .sharepoint_update_bar import register_sharepoint_bar_callbacks


def register_callbacks(app, app_state):
    register_headers_callbacks(app, app_state)
    register_cards_callbacks(app, app_state)
    register_sharepoint_bar_callbacks(app, app_state)
