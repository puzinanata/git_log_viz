import pandas as pd
import plotly.express as px


def graph_type_1(
        df: pd,
        fig_file_name: str,
        column_name_date: str,
        title: str,
        dtick: str,
        tickformat=None):
    count = df.groupby(column_name_date)['commit'].count().reset_index()
    count.columns = [column_name_date, 'commit_count']
    fig1 = px.line(count, x=column_name_date, y='commit_count', title=title, markers=True)

    fig1.update_layout(
    title_x=0.5,
    xaxis=dict(
            tickmode='linear',
            tick0=count[column_name_date].min(),
            dtick=dtick,
            tickformat=tickformat
    )
    )

    fig1.write_image(fig_file_name, width=1424, height=450, scale=2)
    return fig1.to_json()
