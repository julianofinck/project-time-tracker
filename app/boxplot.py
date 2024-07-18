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
        title="Boxplot de horas trabalhadas por pessoa",
        xaxis_title='Pessoa',
        yaxis_title='Horas',
        #boxmode='group'  # group together boxes of the different traces for each value of x
        showlegend=False,
        annotations=[
            dict(
                text="(Há algumas horas claradas no banco de forma errada, por isso os valores negativos.)",
                xref='paper', yref='paper',
                x=0.5, y=1.45,  # Adjust y to position the annotation at the bottom
                showarrow=False,
                font=dict(size=12),
                xanchor='center',
                yanchor='top'
            )
        ]
    )

    return fig