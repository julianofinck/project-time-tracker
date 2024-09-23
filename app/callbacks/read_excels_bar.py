import threading

from dash import Input, Output, State

from app import app, app_state
from app.languages.translator import translator

# Global progress variable
progress = 0
running_thread = False


# Callback to start the background process
@app.callback(
    Output("interval-component", "disabled"),
    Output("update-button", "n_clicks"),
    Output("update-bar-loading", "style"),
    Output("progress-text", "children"),
    Input("interval-component", "n_intervals"),
    Input("update-button", "n_clicks"),
    State("update-bar-loading", "style"),
)
def start_update(n_intervals, n_clicks, style):
    global progress, running_thread

    progress = app_state.progress  # 140271963898160

    style["width"] = f"{progress}%"

    if n_clicks not in (None, 0) and not running_thread:
        threading.Thread(target=app_state.get_dfs).start()
        running_thread = True
        app_state.progress = 0
        return False, None, style, f"{app_state.progress}%"
    elif running_thread and progress < 99:
        return False, None, style, f"{app_state.progress}%"
    elif n_intervals > 10:
        running_thread = False
        app_state.progress = 0
        style["width"] = f"100%"
        return True, None, style, translator.translate("Updated!")
    else:
        return True, None, style, f""
