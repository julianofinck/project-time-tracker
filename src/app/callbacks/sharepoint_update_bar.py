# Global progress variable
progress = 0
running_thread = False


def register_sharepoint_bar_callbacks(app, app_state):
    import threading

    from dash import Input, Output, State


    @app.callback(
        Output("interval-component", "disabled"),
        Output("update-button", "n_clicks"),
        Output("update-bar-loading", "style"),
        Output("progress-text", "children"),
        Output("reload-flag", "data"),  # <-- ADD THIS
        Input("interval-component", "n_intervals"),
        Input("update-button", "n_clicks"),
        State("update-bar-loading", "style"),
    )
    def start_update(n_intervals, n_clicks, style):
        global progress, running_thread

        progress = app_state.progress
        style["width"] = f"{progress}%"

        if n_clicks not in (None, 0) and not running_thread:
            threading.Thread(target=app_state.get_dfs).start()
            running_thread = True
            app_state.progress = 0
            return False, None, style, f"{app_state.progress}%", {"reload": False}
        elif running_thread and progress < 99:
            return False, None, style, f"{app_state.progress}%", {"reload": False}
        elif n_intervals > 10:
            running_thread = False
            app_state.progress = 0
            style["width"] = "100%"
            return (
                True,
                None,
                style,
                "Updated!",
                {"reload": True},
            )  # <-- THIS triggers reload
        else:
            return True, None, style, "", {"reload": False}
