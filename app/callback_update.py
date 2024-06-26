import threading

from dash import Input, Output, State

from . import app
from .__init__ import data_importer

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

    progress = data_importer.progress  # 140271963898160

    style["width"] = f"{progress}%"

    if n_clicks not in (None, 0) and not running_thread:
        threading.Thread(target=data_importer.get_dfs).start()
        running_thread = True
        return False, None, style, f"{int(progress)}%"
    elif running_thread and progress < 99:
        return False, None, style, f"{int(progress)}%"
    elif n_intervals > 10:
        running_thread = False
        data_importer.progress = 0
        style["width"] = f"100%"
        return True, None, style, f"Atualizado!"
    else:
        return True, None, style, f""
