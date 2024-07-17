import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd


def boxplot(data: pd.DataFrame) -> go.Figure:
    df = data[["colleague", "date", "hours"]].groupby(by=["colleague", "date"], as_index=False).sum()
 
    # Create the boxplot
    fig = go.Figure()

    for colleague in df['colleague'].unique():
        fig.add_trace(go.Box(
            y=df[df['colleague'] == colleague]['hours'],
            name=colleague,
            boxpoints=False,  # show all points
            jitter=0.5,       # spread out the points
            pointpos=-1.8,    # offset points to the left
            showlegend=False,
        ))

    fig.update_layout(
        xaxis_title='Colleague',
        yaxis_title='Hours',
        #boxmode='group'  # group together boxes of the different traces for each value of x
        showlegend=False,
    )

    return fig