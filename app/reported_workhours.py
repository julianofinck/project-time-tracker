import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import datetime


def reported_workhours(data: pd.DataFrame) -> go.Figure:
    """
    Get the number of workdays and the number of filled days
    """
    df = data[["colleague", "date", "hours"]].groupby(by=["colleague", "date"], as_index=False).sum()
 
    # Create the boxplot
    fig = go.Figure()

    today = datetime.datetime.now().date()

    report = list()
    for colleague in df['colleague'].unique():
        view = df[df["colleague"] == colleague]
        first_day = view["date"].min()
        weekdays = count_weekdays(first_day, today)
        reported_weekdays = len(view)
        clt_workhours = reported_weekdays * 8.5
        reported_workhours = round(view["hours"].sum(), 2)

        report.append({
            "colleague": colleague,
            "first_day": first_day,
            "weekdays": weekdays,
            "reported_weekdays": len(view),
            "clt_workhours": clt_workhours,
            "reported_workhous": reported_workhours,
        })
    df = pd.DataFrame(report)

        # Calculate percentages
    df['reported_weekdays_pct'] = df['reported_weekdays'] / df['weekdays'] * 100
    df['non_reported_weekdays_pct'] = 100 - df['reported_weekdays_pct']
    df['reported_workhours_pct'] = df['reported_workhous'] / df['clt_workhours'] * 100
    df['non_reported_workhours_pct'] = 100 - df['reported_workhours_pct']

    # Create traces for weekdays
    weekdays_trace_reported = go.Bar(
        x=df['colleague'],
        y=df['reported_weekdays_pct'],
        name='Dias úteis<br>reportados',
        marker_color='green',
        hovertemplate='%{y:.2f}%<br>(%{text})',
        text=[f"{rw}/{wd}" for rw, wd in zip(df['reported_weekdays'], df['weekdays'])]
    )

    weekdays_trace_non_reported = go.Bar(
        x=df['colleague'],
        y=df['non_reported_weekdays_pct'],
        name='Dias úteis<br>não-reportados',
        marker_color='red',
        hovertemplate='%{y:.2f}%<br>(%{text})',
        text=[f"{round(wd-rw, 2)}/{wd}" for rw, wd in zip(df['reported_weekdays'], df['weekdays'])]
    )

    # Create traces for workhours
    workhours_trace_reported = go.Bar(
        x=df['colleague'],
        y=df['reported_workhours_pct'],
        name='Horas<br>reportadas',
        marker_color='green',
        hovertemplate='%{y:.2f}%<br>(%{text})',
        text=[f"{rw}/{cw}" for rw, cw in zip(df['reported_workhous'], df['clt_workhours'])]
    )

    workhours_trace_non_reported = go.Bar(
        x=df['colleague'],
        y=df['non_reported_workhours_pct'],
        name='Horas não<br>reportadas',
        marker_color='red',
        hovertemplate='%{y:.2f}%<br>(%{text})',
        text=[f"{round(cw-rw, 2)}/{cw}" for rw, cw in zip(df['reported_workhous'], df['clt_workhours'])]
    )

    # Combine traces
    fig = go.Figure(data=[
        weekdays_trace_reported,
        weekdays_trace_non_reported,
        workhours_trace_reported,
        workhours_trace_non_reported
    ])

    # Update layout
    fig.update_layout(
        barmode='stack',
        title='Horas e dias úteis reportados vs não-reportados',
        xaxis_title='Pessoa',
        yaxis_title='Porcentagens',
        showlegend=False,
        annotations=[
            dict(
                text="(Os dias são contados a partir do registro válido mais antigo. O programa ainda está considerando feriado um dia útil. É considerado que todas as pessoas façam 8,5 horas por dia.)",
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


import numpy as np

def count_weekdays(start_date, end_date):
    weekdays = np.busday_count(start_date, end_date)
    return weekdays
