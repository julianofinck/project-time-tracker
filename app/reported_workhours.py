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
        name='Reported Weekdays',
        marker_color='green',
        hovertemplate='%{y:.2f}%<br>(%{text})',
        text=[f"{rw}/{wd}" for rw, wd in zip(df['reported_weekdays'], df['weekdays'])]
    )

    weekdays_trace_non_reported = go.Bar(
        x=df['colleague'],
        y=df['non_reported_weekdays_pct'],
        name='Non-reported Weekdays',
        marker_color='red',
        hovertemplate='%{y:.2f}%<br>(%{text})',
        text=[f"{wd-rw}/{wd}" for rw, wd in zip(df['reported_weekdays'], df['weekdays'])]
    )

    # Create traces for workhours
    workhours_trace_reported = go.Bar(
        x=df['colleague'],
        y=df['reported_workhours_pct'],
        name='Reported Workhours',
        marker_color='green',
        hovertemplate='%{y:.2f}%<br>(%{text})',
        text=[f"{rw}/{cw}" for rw, cw in zip(df['reported_workhous'], df['clt_workhours'])]
    )

    workhours_trace_non_reported = go.Bar(
        x=df['colleague'],
        y=df['non_reported_workhours_pct'],
        name='Non-reported Workhours',
        marker_color='red',
        hovertemplate='%{y:.2f}%<br>(%{text})',
        text=[f"{cw-rw}/{cw}" for rw, cw in zip(df['reported_workhous'], df['clt_workhours'])]
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
        title='Reported vs Non-reported Weekdays and Workhours',
        xaxis_title='Colleague',
        yaxis_title='Percentage',
        showlegend=False
    )
    
    return fig


import numpy as np

def count_weekdays(start_date, end_date):
    weekdays = np.busday_count(start_date, end_date)
    return weekdays
