import datetime

import dash
import numpy as np
import pandas as pd
import plotly.graph_objs as go


def last_reported_day(data: pd.DataFrame, no_valid_register) -> go.Figure:
    df = data

    # Get date of last filled day and groupby day
    df = df[["colleague", "date"]].groupby(by="colleague", as_index=False).max()

    # Group by date
    df = df.groupby("date", as_index=False)["colleague"].apply(", ".join)

    # Count quantity
    df["quantity"] = df["colleague"].apply(lambda x: x.count(",") + 1)

    # Add colleague who never filled the table properly as well
    if no_valid_register:
        no_valid_register.sort()
        min_date = df["date"].min() - datetime.timedelta(1)
        texto = "Sem registro válido:<br>" + ", ".join(no_valid_register)
        df.iloc[-1] = [min_date, texto, len(no_valid_register)]

    # Adjust hasty employees
    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(1)
    hasty_mask = df["date"] > today
    hasty_df = df[hasty_mask]
    if not hasty_df.empty:
        quantity = hasty_df["quantity"].sum()
        texto = [
            f"{row['colleague']} ({row['date'].strftime('%Y-%m-%d')})"
            for _, row in hasty_df.iterrows()
        ]
        texto = "Colegas do Futuro:<br>" + "<br>".join(texto)

        # Remove hasty
        df = df[~hasty_mask].reset_index(drop=True)

        # Add new register for visualizaiton
        df.loc[len(df)] = [tomorrow, texto, quantity]

        # Count
        df.groupby("date").size().reset_index(name="quantity")

    # Order dataframe by date
    df = df.sort_values(by="date").reset_index(drop=True)

    # Graph settings
    start_date = df["date"].min() - datetime.timedelta(1)
    end_date = tomorrow + datetime.timedelta(1)

    # Create layout for histogram
    layout = go.Layout(
        xaxis=dict(tickangle=-35, tickfont=dict(size=8), range=[start_date, end_date]),
        # paper_bgcolor='lightgrey',  # Background color of the entire paper
        plot_bgcolor="lightgrey",  # Background color of the plotting area
        margin=dict(l=14, r=14, b=14, t=14, pad=5),
    )
    # TODO: Change the hardcoded "7" for something more responsive

    # Get colors
    colors = ["#198238"] * len(df)
    if no_valid_register:
        colors[0] = "red"
    if not hasty_df.empty:
        colors[-1] = "#A47300"

    # Create histogram
    hist_data = [
        go.Bar(
            x=df["date"],
            y=df["quantity"],
            text=df["quantity"],
            hovertemplate=[
                f"{v} <br>{k}<extra></extra>"
                for k, v in zip(df["date"], df["colleague"])
            ],  # Full x-values in hovertemplate
            marker=dict(
                color=colors,  # Color hex code
            ),
        )
    ]

    # Create figure
    figure = go.Figure(data=hist_data, layout=layout)

    return figure


def boxplot(data: pd.DataFrame) -> go.Figure:
    df = (
        data[["colleague", "date", "hours"]]
        .groupby(by=["colleague", "date"], as_index=False)
        .sum()
    )

    # Create the boxplot
    fig = go.Figure()

    for colleague in df["colleague"].unique():
        fig.add_trace(
            go.Box(
                y=df[df["colleague"] == colleague]["hours"],
                name=colleague,
                boxpoints=False,  # show all points
                jitter=0.5,  # spread out the points
                pointpos=-1.8,  # offset points to the left
                showlegend=False,
            )
        )

    fig.update_layout(
        title="Boxplot de horas trabalhadas por pessoa",
        xaxis_title="Pessoa",
        yaxis_title="Horas",
        # boxmode='group'  # group together boxes of the different traces for each value of x
        showlegend=False,
        annotations=[
            dict(
                text="(Há algumas horas claradas no banco de forma errada, por isso os valores negativos.)",
                xref="paper",
                yref="paper",
                x=0.5,
                y=1.45,  # Adjust y to position the annotation at the bottom
                showarrow=False,
                font=dict(size=12),
                xanchor="center",
                yanchor="top",
            )
        ],
    )

    return fig


def reported_workhours(data: pd.DataFrame) -> go.Figure:
    """
    Get the number of workdays and the number of filled days
    """
    df = (
        data[["colleague", "date", "hours"]]
        .groupby(by=["colleague", "date"], as_index=False)
        .sum()
    )

    # Create the boxplot
    fig = go.Figure()

    today = datetime.datetime.now().date()

    report = list()
    for colleague in df["colleague"].unique():
        view = df[df["colleague"] == colleague]
        first_day = view["date"].min()
        weekdays = count_weekdays(first_day, today)
        reported_weekdays = len(view)
        clt_workhours = reported_weekdays * 8.5
        reported_workhours = round(view["hours"].sum(), 2)

        report.append(
            {
                "colleague": colleague,
                "first_day": first_day,
                "weekdays": weekdays,
                "reported_weekdays": len(view),
                "clt_workhours": clt_workhours,
                "reported_workhous": reported_workhours,
            }
        )
    df = pd.DataFrame(report)

    # Calculate percentages
    df["reported_weekdays_pct"] = df["reported_weekdays"] / df["weekdays"] * 100
    df["non_reported_weekdays_pct"] = 100 - df["reported_weekdays_pct"]
    df["reported_workhours_pct"] = df["reported_workhous"] / df["clt_workhours"] * 100
    df["non_reported_workhours_pct"] = 100 - df["reported_workhours_pct"]

    # Create traces for weekdays
    weekdays_trace_reported = go.Bar(
        x=df["colleague"],
        y=df["reported_weekdays_pct"],
        name="Dias úteis<br>reportados",
        marker_color="green",
        hovertemplate="%{y:.2f}%<br>(%{text})",
        text=[f"{rw}/{wd}" for rw, wd in zip(df["reported_weekdays"], df["weekdays"])],
    )

    weekdays_trace_non_reported = go.Bar(
        x=df["colleague"],
        y=df["non_reported_weekdays_pct"],
        name="Dias úteis<br>não-reportados",
        marker_color="red",
        hovertemplate="%{y:.2f}%<br>(%{text})",
        text=[
            f"{round(wd-rw, 2)}/{wd}"
            for rw, wd in zip(df["reported_weekdays"], df["weekdays"])
        ],
    )

    # Create traces for workhours
    workhours_trace_reported = go.Bar(
        x=df["colleague"],
        y=df["reported_workhours_pct"],
        name="Horas<br>reportadas",
        marker_color="green",
        hovertemplate="%{y:.2f}%<br>(%{text})",
        text=[
            f"{rw}/{cw}" for rw, cw in zip(df["reported_workhous"], df["clt_workhours"])
        ],
    )

    workhours_trace_non_reported = go.Bar(
        x=df["colleague"],
        y=df["non_reported_workhours_pct"],
        name="Horas não<br>reportadas",
        marker_color="red",
        hovertemplate="%{y:.2f}%<br>(%{text})",
        text=[
            f"{round(cw-rw, 2)}/{cw}"
            for rw, cw in zip(df["reported_workhous"], df["clt_workhours"])
        ],
    )

    # Combine traces
    fig = go.Figure(
        data=[
            weekdays_trace_reported,
            weekdays_trace_non_reported,
            workhours_trace_reported,
            workhours_trace_non_reported,
        ]
    )

    # Update layout
    fig.update_layout(
        barmode="stack",
        title="Horas e dias úteis reportados vs não-reportados",
        xaxis_title="Pessoa",
        yaxis_title="Porcentagens",
        showlegend=False,
        annotations=[
            dict(
                text="(Os dias são contados a partir do registro válido mais antigo. O programa ainda está considerando feriado um dia útil. É considerado que todas as pessoas façam 8,5 horas por dia.)",
                xref="paper",
                yref="paper",
                x=0.5,
                y=1.45,  # Adjust y to position the annotation at the bottom
                showarrow=False,
                font=dict(size=12),
                xanchor="center",
                yanchor="top",
            )
        ],
    )

    return fig


def count_weekdays(start_date, end_date) -> int:
    weekdays = np.busday_count(start_date, end_date)
    return weekdays
