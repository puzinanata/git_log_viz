import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go


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


def graph_heatmap(
        df,
        fig_file_name: str,
        hour: str,
        author: str,
        num_top: int,
        title_user: str,
        title_period,
        mode: str):

    if mode == "top_authors":
        commit_count = df.groupby([hour, author]).size().unstack(fill_value=0)
        top_x_authors = commit_count.sum(axis=0).nlargest(num_top).index
        commit_count_top = commit_count[top_x_authors]
        commit_count_top_percent = commit_count_top.div(commit_count_top.sum(axis=0), axis=1) * 100

        df_long = commit_count_top_percent.reset_index().melt(
            id_vars=hour,
            var_name=author,
            value_name='percentage'
        )

        y_axis_title = title_user
        category_order = top_x_authors[::-1]

    else:
        commit_count_all = df.groupby(hour).size()
        commit_count_all_percent = (commit_count_all / commit_count_all.sum()) * 100

        df_long = commit_count_all_percent.reset_index()
        df_long.columns = [hour, 'percentage']
        df_long[author] = title_user

        y_axis_title = ""
        category_order = [title_user]

    fig = px.density_heatmap(
        df_long,
        x=hour,
        y=author,
        z="percentage",
        histfunc="sum",
        color_continuous_scale="YlGnBu",
        title=f"Distribution of Commits by Hour for {title_user} (as Percentage) for {title_period}",
    )

    # Add text annotations using a scatter plot
    fig.add_trace(
        go.Scatter(
            x=df_long[hour],
            y=df_long[author],
            text=df_long["percentage"].round(0).astype(int),
            mode="text",
            textposition="middle center",
            textfont=dict(size=12, color="black"),
        )
    )

    fig.update_xaxes(type='category', title="Hour of the Day", tickmode="linear", dtick=1)
    fig.update_layout(
        yaxis=dict(categoryorder="array", categoryarray=category_order),
        title_x=0.5,
        yaxis_title=y_axis_title,
        coloraxis_colorbar_title="Percentage"
    )

    fig.write_image(fig_file_name, width=1409, height=450, scale=2)
    return fig.to_json()
