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
        num_top: int,
        counter: str,
        column_name: str):

    commit_count = df.groupby([column_name_date, author]).size().reset_index(name='commit_count')
    total_commit_by_author = commit_count.groupby(author)['commit_count'].sum()
    total_changes_by_author = df.groupby(author)['num_changes'].sum()

    if counter == "commit_count":
        top_x_authors = total_commit_by_author.sort_values(ascending=False).head(num_top)
        total_count = total_commit_by_author.sum()
    else:
        top_x_authors = total_changes_by_author.sort_values(ascending=False).head(num_top)
        total_count = total_changes_by_author.sum()

    table_data = {
        "Rank": list(range(1, len(top_x_authors) + 1)),
        "Author": top_x_authors.index.tolist(),
        f"{column_name}": [f"{value:,}".replace(",", " ") for value in (top_x_authors.values.tolist())],
        "Share of Author in %": (top_x_authors.values/total_count * 100).round(0).astype(int).tolist()
    }

    fig = ff.create_table([list(table_data.keys())] + list(zip(*table_data.values())))

    fig.write_image(fig_file_name, width=1424, height=450, scale=2)
    return fig.to_json()


def graph_bar_line(
        df: pd,
        fig_file_name: str,
        column_name_date: str,
        title: str,
        dtick: str):
    df_summary = df.groupby(column_name_date).agg(
        unique_users=("username", "nunique"),
        total_commits=("commit", "count")
    ).reset_index()

    fig = px.bar(
        df_summary,
        x=column_name_date,
        y="total_commits",
        text_auto=True,
        title=title,
        labels={"total_commits": "Total Commits", column_name_date: column_name_date}
    )
    fig.update_traces(textposition="outside")

    # Add line for unique usernames
    fig.add_scatter(
        x=df_summary[column_name_date],
        y=df_summary["unique_users"],
        mode="lines+markers+text",
        name="Total authors",
        yaxis="y2",
        text=df_summary["unique_users"],
        textposition="top center",
        textfont=dict(color="red"),
    )

    # Update layout for dual-axis
    fig.update_layout(
        yaxis=dict(title="Total Commits"),
        yaxis2=dict(title="Authors", overlaying="y", side="right"),
        title_x=0.5,
        xaxis=dict(
            tickmode='linear',
            tick0=df_summary[column_name_date].min(),
            dtick=dtick
        )
    )
    fig.write_image(fig_file_name, width=1424, height=450, scale=2)
    return fig.to_json()


def graph_pie(
        df,
        fig_file_name: str,
        column_name_date: str,
        title: str,
        author: str,
        num_top: int,
        counter: str,
        title_date: str):

    commit_count = df.groupby([column_name_date, author]).size().reset_index(name='commit_count')
    total_commit_by_author = commit_count.groupby(author)['commit_count'].sum()
    total_changes_by_author = df.groupby(author)['num_changes'].sum()

    if counter == 'commit_count':
        top_x_authors = total_commit_by_author.sort_values(ascending=False).head(num_top)
        others = total_commit_by_author.sum() - top_x_authors.sum()
    else:
        top_x_authors = total_changes_by_author.sort_values(ascending=False).head(num_top)
        others = total_changes_by_author.sum() - top_x_authors.sum()

    if others > 0:
        top_x_authors['Others'] = others

    data = top_x_authors.reset_index()
    data.columns = ['Author', counter]

    fig = px.pie(
        data,
        values=counter,
        names='Author',
        title=f"Top {num_top} Authors by {title} {title_date}"
    )

    fig.write_image(fig_file_name, scale=2)
    return fig.to_json()


def graph_line_author(
        df,
        fig_file_name: str,
        column_name_date: str,
        author: str,
        num_top: str,
        title: str,
        dtick: str):

    commit_count = df.groupby([column_name_date, author]).size().reset_index(name='commit_count')
    total_commits_by_author = commit_count.groupby(author)['commit_count'].sum()
    top_authors = total_commits_by_author.nlargest(num_top).index
    top_commit_count = commit_count[commit_count[author].isin(top_authors).sort_values(ascending=False)]
    counter = df.groupby(column_name_date)['commit'].count().reset_index()

    fig = px.line(
        top_commit_count,
        x=column_name_date,
        y="commit_count",
        color=author,
        title=f"Count of commits by top authors {title}",
        markers=True)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        title_x=0.5,
        showlegend=True,
        xaxis=dict(
            tickmode='linear',
            tick0=counter[column_name_date].min(),
            dtick=dtick
        )
    )

    fig.write_image(fig_file_name, width=1409, height=450, scale=2)
    return fig.to_json()
