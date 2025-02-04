import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

def graph_line(
        df: pd,
        fig_file_name: str,
        column_name_date: str,
        title: str,
        dtick: str):
    count = df.groupby(column_name_date)['commit'].count().reset_index()
    count.columns = [column_name_date, 'commit_count']
    fig = px.line(count, x=column_name_date, y='commit_count', title=title, markers=True)

    fig.update_layout(
        title_x=0.5,
        xaxis=dict(
            tickmode='linear',
            tick0=count[column_name_date].min(),
            dtick=dtick
        )
    )

    fig.write_image(fig_file_name, width=1424, height=450, scale=2)
    return fig.to_json()

def graph_table(
        df: pd,
        fig_file_name: str,
        column_name_date: str,
        author: str,
        num_top: int
):
    commit_counts = df.groupby([column_name_date, author]).size().reset_index(name='commit_count')
    total_commits_by_email = commit_counts.groupby(author)['commit_count'].sum()
    top_x_emails = total_commits_by_email.sort_values(ascending=False).head(num_top)

    total_commits = total_commits_by_email.sum()

    table_data = {
    "Rank": list(range(1, len(top_x_emails) + 1)),
    "Author": top_x_emails.index.tolist(),
    "Total Commits": [f"{value:,}".replace(",", " ") for value in (top_x_emails.values.tolist())],
    "Share of Author in %": (top_x_emails.values/total_commits * 100).round(0).astype(int).tolist()
    }

    fig = ff.create_table([list(table_data.keys())] + list(zip(*table_data.values())))

    fig.write_image(fig_file_name, width=1424, height=450, scale=2)
    return fig.to_json()

