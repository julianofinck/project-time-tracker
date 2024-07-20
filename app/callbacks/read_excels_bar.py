import threading

from dash import Input, Output, State

from app import app, app_state

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
    # print(f"n_intervals: {n_intervals}\n", f"n_clicks: {n_clicks}\n", f"style: {style}\n", f"running_thread: {running_thread}\n",)

    if n_clicks not in (None, 0) and not running_thread:
        threading.Thread(target=app_state.get_dfs).start()
        running_thread = True
        return False, None, style, f"{int(progress)}%"
    elif running_thread and progress < 99:
        return False, None, style, f"{int(progress)}%"
    elif n_intervals > 10:
        running_thread = False
        app_state.progress = 0
        style["width"] = f"100%"
        return True, None, style, f"Atualizado!"
    else:
        return True, None, style, f""
