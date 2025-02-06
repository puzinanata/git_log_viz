import subprocess
import re
import os
import plotly.express as px
import pandas as pd
from src import settings
from src import templates
from src import graph
import plotly.graph_objects as go

# Command to extract data from git log
command = "git log --pretty=format:'%H %ad %ae' --stat --no-merges"

# Dictionary to store the log data for each repository
repo_logs = {}

# Loop for iteration through repos
for repo_path, repo_csv in zip(settings.repo_name, settings.repo_log_csv):

    if not os.path.exists(repo_csv):
        print(f"DB csv file '{repo_csv}' doesn't exist.")
        result = subprocess.run(
            f"cd {repo_path}; {command}",
            shell=True,
            text=True,
            capture_output=True
        )
        if result.returncode == 0:
            repo_logs[repo_path] = result.stdout
        else:
            print(f"Error retrieving data from {repo_path}: {result.stderr}")
    else:
        print(f"DB csv file '{repo_csv}' exist so do it fast.")


# Process the output

# Regex to match commit details and the summary line

# commit_pattern covers following cases:
# 47b679341b5d2051cce591af65f51e22be051c28 Fri Dec 27 12:16:48 2024 +0300 user@example.com
# 47b679341b5d2051cce591af65f51e22be051c28 Fri Dec 27 12:16:48 2024 -0300 user@example.com
# 47b679341b5d2051cce591af65f51e22be051c28 Fri Dec 27 12:16:48 2024 0000 user@example.com
# 00a9376311c94680e83bdd05f5e9d398869a2bd7 Wed Sep 7 22:38:54 2022 +0300 user@example.com
commit_pattern = r"^([a-f0-9]{40})\s+(\S+ \S+ \d+ [0-9:]{8} [0-9]{4} .?[0-9\+\-]{4}) (.*)"

#  summary_pattern covers following cases:
#  2 files changed, 0 insertions(+), 0 deletions(-)
#  2 files changed, 0 insertions(+)
#  2 files changed, 0 deletions(-)
#  2 file changed, 0 insertions(+), 0 deletions(-)
#  2 file changed, 0 insertions(+)
#  2 file changed, 0 deletions(-)
summary_pattern = r"(\d+) files? \S+, (\d+) \S+?\([\+\-]\),? ?(\d+)?"
hour_pattern = r"(\d{2}):\d{2}:\d{2}"

commits = {}

# Process logs for each repository
for repo_log, log_csv in zip(repo_logs.items(), settings.repo_log_csv):
    log_data = repo_log[1]
    repo = repo_log[0]
    lines = log_data.splitlines()
    commits[log_csv] = []

    for line in lines:
        commit_match = re.match(commit_pattern, line)
        summary_match = re.search(summary_pattern, line)

        if commit_match:
            timestamp = commit_match.group(2)
            hour_match = re.search(hour_pattern, timestamp)

            commits[log_csv].append({
                "repo": repo,
                "commit": commit_match.group(1),
                "date": commit_match.group(2),
                "hour": int(hour_match.group(1)) if hour_match else 0,
                "email": commit_match.group(3),
                "num_changes": 0,
            })
        elif summary_match and commits[log_csv]:
            num_insertions = int(summary_match.group(2)) if summary_match.group(2) else 0
            num_deletions = int(summary_match.group(3)) if summary_match.group(3) else 0
            commits[log_csv][-1]["num_changes"] = num_insertions + num_deletions

    # Save git log from repo to separate CSV file
    pd.DataFrame(commits[log_csv]).to_csv(log_csv, index=False)

# Read data from cvs
df = pd.concat([pd.read_csv(file) for file in settings.repo_log_csv], ignore_index=True)


# Section of Data preparation and creation new attributes in df
df["date"] = pd.to_datetime(df["date"], utc=True)

df["year"] = df["date"].dt.year
df["year"] = df["year"].astype(int)

df["utc_hour"] = df["date"].dt.hour

df["month_year"] = df["date"].dt.strftime('%Y-%m')
df['month_year'] = pd.to_datetime(df['month_year'], format='%Y-%m')

# Extract the part before '@' to create new column 'Username'
df['username'] = df['email'].str.split('@').str[0]

# Exclude the username
df = df[~df['username'].isin(settings.exclude_username)]

# Replace all occurrences of old username with new username
df['username'] = df['username'].replace(settings.old_username, settings.new_username)

# Transfer username to lower case
df['username'] = df['username'].str.lower()

# Filter years
df = df[(df['date'].dt.year >= settings.start_year) & (df['date'].dt.year <= settings.finish_year)]

# Filter last year and creation filtered df with data fot the last year
last_year = pd.Timestamp.today().year - 1
last_year_df = df[df['month_year'].dt.year == last_year]

# Section of graphs building

# Building line chart with total commits by year.
fig1_json = graph.graph_line(
    df,
    "result/fig1.png",
    "year",
    "Count of commits by Year",
    '1'
)

# Building line chart with total commits in last year.
fig4_json = graph.graph_line(
    last_year_df,
    "result/fig4.png",
    "month_year",
    "Count of commits in last year",
    'M1'
)

# Building graph table with top authors by count the commits for all years
fig2_json = graph.graph_table(
    df,
    "result/fig2.png",
    'year',
    settings.author,
    settings.num_top,
    'commit_count',
    "Total Commits"
)

# Building graph table with top authors by count the commits in last year
fig5_json = graph.graph_table(
    last_year_df,
    "result/fig5.png",
    'month_year',
    settings.author,
    settings.num_top,
    'commit_count',
    "Total Commits"
)

# Building graph table with top authors by sum of changes for all years
fig7_json = graph.graph_table(
    df,
    "result/fig7.png",
    'year',
    settings.author,
    settings.num_top,
    'num_changes',
    "Total Changes (insertions+deletions)"
)

# Building graph table with top authors by sum of changes for last year
fig8_json = graph.graph_table(
    last_year_df,
    "result/fig8.png",
    'month_year',
    settings.author,
    settings.num_top,
    'num_changes',
    "Total Changes (insertions+deletions)"
)

# Building bar&line chart by number of authors and commits by year
fig13_json = graph.graph_bar_line(
    df,
    "result/fig13.png",
    'year',
    "Number of Authors and Total Commits by Year",
    '1'
)

# Building bar&line chart by number of authors and commits in last year
fig14_json = graph.graph_bar_line(
    last_year_df,
    "result/fig14.png",
    'month_year',
    "Number of Authors and Total Commits in Last Year",
    'M1'
)

# Building pie chart by commit share of top authors for all years
fig2a_json = graph.graph_pie(
    df,
    "result/fig2a.png",
    'year',
    "Commit Count",
    settings.author,
    settings.num_top,
    'commit_count',
    "for All Years"
)

# Building pie chart by changes share of top authors for all years
fig7b_json = graph.graph_pie(
    df,
    "result/fig7b.png",
    'year',
    "Share of Changes",
    settings.author,
    settings.num_top,
    'num_changes',
    "for All Years"
)

# Building pie chart by commit share of top authors in last year
fig5a_json = graph.graph_pie(
    last_year_df,
    "result/fig5a.png",
    'month_year',
    "Commit Count",
    settings.author,
    settings.num_top,
    'commit_count',
    "in Last Year"
)

# Building pie chart by changes share of top authors in last year
fig8b_json = graph.graph_pie(
    last_year_df,
    "result/fig8b.png",
    'month_year',
    "Share of Changes",
    settings.author,
    settings.num_top,
    'num_changes',
    "in Last Year"
)

# Building line chart  by top authors by year
fig3_json = graph.graph_line_author(
    df,
    "result/fig3.png",
    'year',
    settings.author,
    settings.num_top,
    "by Year",
    '1'
)

# Building line chart  by top authors in last year
fig6_json = graph.graph_line_author(
    last_year_df,
    "result/fig6.png",
    'month_year',
    settings.author,
    settings.num_top,
    "in Last Year",
    'M1'
)

# Building heatmap graph with distribution commits by hours by top authors for all years

# Aggregate commits by hour
commit_counts = df.groupby(settings.hour).size()
commit_counts_all_percent = (commit_counts / commit_counts.sum()) * 100

df_all = commit_counts_all_percent.reset_index()
df_all.columns = [settings.hour, 'percentage']
df_all['author'] = 'All Users'

# Create heatmap using Plotly
fig12 = px.density_heatmap(
    df_all,
    x=settings.hour,
    y='author',
    z="percentage",
    color_continuous_scale="YlGnBu",
    title="Distribution of Commits by Hour for All Authors (as Percentage) for All Years",
)

# Add text annotations using a scatter plot
fig12.add_trace(go.Scatter(
    x=df_all[settings.hour],
    y=df_all['author'],
    text=df_all["percentage"].round(0).astype(int),
    mode="text",
    textposition="middle center",
    textfont=dict(size=12, color="black"),
    )
)

fig12.update_xaxes(type='category', title="Hour of the Day", tickmode="linear", dtick=1)

fig12.update_layout(
    title_x=0.5,
)

fig12.write_image("result/fig12.png", width=1409, height=450, scale=2)
fig12_json = fig12.to_json()

# Building heatmap graph with distribution commits by hours by top authors by last year

# Aggregate commits by hour and author
commit_counts = last_year_df.groupby([settings.hour, settings.author]).size().unstack(fill_value=0)
top_x_authors = commit_counts.sum(axis=0).nlargest(settings.num_top).index
commit_counts_top10 = commit_counts[top_x_authors]
commit_counts_top10_percent = commit_counts_top10.div(commit_counts_top10.sum(axis=0), axis=1) * 100

df_long = commit_counts_top10_percent.reset_index().melt(
    id_vars=settings.hour,
    var_name=settings.author,
    value_name='percentage'
)

# Create heatmap using Plotly
fig10 = px.density_heatmap(
    df_long,
    x=settings.hour,
    y=settings.author,
    z="percentage",
    histfunc="sum",
    color_continuous_scale="YlGnBu",
    title="Distribution of Commits by Hour for Top Authors (as Percentage) for the last year",
)

# Add text annotations using a scatter plot
fig10.add_trace(
    go.Scatter(
        x=df_long[settings.hour],
        y=df_long[settings.author],
        text=df_long["percentage"].round(0).astype(int),
        mode="text",
        textposition="middle center",
        textfont=dict(size=12, color="black"),
    )
)

fig10.update_xaxes(type='category', title="Hour of the Day", tickmode="linear", dtick=1)
fig10.update_layout(
    yaxis=dict(categoryorder="array", categoryarray=top_x_authors[::-1]),
    title_x=0.5,
    yaxis_title="Author",
    coloraxis_colorbar_title="Percentage"
)

fig10.write_image("result/fig10.png", width=1409, height=450, scale=2)
fig10_json = fig10.to_json()

# Building heatmap graph with distribution commits by hours by top authors by last year

# Aggregate commits by hour
commit_counts_12m = last_year_df.groupby(settings.hour).size()
commit_counts_all_percent = (commit_counts_12m / commit_counts_12m.sum()) * 100

df_all = commit_counts_all_percent.reset_index()
df_all.columns = [settings.hour, 'percentage']
df_all['author'] = 'All Users'

# Create heatmap using Plotly
fig11 = px.density_heatmap(
    df_all,
    x=settings.hour,
    y='author',
    z="percentage",
    color_continuous_scale="YlGnBu",
    title="Distribution of Commits by Hour for All Authors (as Percentage) for the last year",
)

# Add text annotations using a scatter plot
fig11.add_trace(go.Scatter(
    x=df_all[settings.hour],
    y=df_all['author'],
    text=df_all["percentage"].round(0).astype(int),
    mode="text",
    textposition="middle center",
    textfont=dict(size=12, color="black"),
    )
)

fig11.update_xaxes(type='category', title="Hour of the Day", tickmode="linear", dtick=1)

fig11.update_layout(
    title_x=0.5,
)

fig11.write_image("result/fig11.png", width=1409, height=450, scale=2)
fig11_json = fig11.to_json()

# Building heatmap graph with distribution commits by hours by top authors by all years

# Aggregate commits by hour and author
commit_counts = df.groupby([settings.hour, settings.author]).size().unstack(fill_value=0)
top_x_authors = commit_counts.sum(axis=0).nlargest(settings.num_top).index
commit_counts_top10 = commit_counts[top_x_authors]
commit_counts_top10_percent = commit_counts_top10.div(commit_counts_top10.sum(axis=0), axis=1) * 100

df_long = commit_counts_top10_percent.reset_index().melt(
    id_vars=settings.hour,
    var_name=settings.author,
    value_name='percentage'
)

# Create heatmap using Plotly
fig9 = px.density_heatmap(
    df_long,
    x=settings.hour,
    y=settings.author,
    z="percentage",
    histfunc="sum",
    color_continuous_scale="YlGnBu",
    title="Distribution of Commits by Hour for Top Authors (as Percentage) for all years",
)

# Add text annotations using a scatter plot
fig9.add_trace(
    go.Scatter(
        x=df_long[settings.hour],
        y=df_long[settings.author],
        text=df_long["percentage"].round(0).astype(int),
        mode="text",
        textposition="middle center",
        textfont=dict(size=12, color="black"),
    )
)

fig9.update_xaxes(type='category', title="Hour of the Day", tickmode="linear", dtick=1)
fig9.update_layout(
    yaxis=dict(categoryorder="array", categoryarray=top_x_authors[::-1]),
    title_x=0.5,
    yaxis_title="Author",
    coloraxis_colorbar_title="Percentage"
)

fig9.write_image("result/fig9.png", width=1409, height=450, scale=2)
fig9_json = fig9.to_json()

# #5. Final Section of generation html reports

# Building of  HTML report with js
html_js_report = (
        templates.head_js_template +
        templates.graph_js_template.format(content=fig1_json, div_name="fig1") +
        templates.graph_js_template.format(content=fig13_json, div_name="fig13") +
        templates.table_js_template.format(content=fig2_json, div_name="fig2") +
        templates.table_js_template.format(content=fig7_json, div_name="fig7") +
        templates.graph_js_double_template.format(
            content1=fig2a_json, content2=fig7b_json, div_name1="fig2a", div_name2="fig7b") +
        templates.graph_js_template.format(content=fig3_json, div_name="fig3") +
        templates.graph_js_template.format(content=fig9_json, div_name="fig9") +
        templates.graph_js_template.format(content=fig12_json, div_name="fig12") +
        templates.graph_js_template.format(content=fig4_json, div_name="fig4") +
        templates.graph_js_template.format(content=fig14_json, div_name="fig14") +
        templates.table_js_template.format(content=fig5_json, div_name="fig5") +
        templates.table_js_template.format(content=fig8_json, div_name="fig8") +
        templates.graph_js_double_template.format(
            content1=fig5a_json, content2=fig8b_json, div_name1="fig5a", div_name2="fig8b") +
        templates.graph_js_template.format(content=fig6_json, div_name="fig6") +
        templates.graph_js_template.format(content=fig10_json, div_name="fig10") +
        templates.graph_js_template.format(content=fig11_json, div_name="fig11") +
        templates.tail_template
              )

# Building of  HTML report with static images
html_image_report = (
        templates.head_template +
        templates.image_template.format(path="fig1.png") +
        templates.image_template.format(path="fig13.png") +
        templates.table_image_template.format(path="fig2.png") +
        templates.table_image_template.format(path="fig7.png") +
        templates.image_double_template.format(path1="fig2a.png", path2="fig7b.png") +
        templates.image_template.format(path="fig3.png") +
        templates.image_template.format(path="fig9.png") +
        templates.image_template.format(path="fig12.png") +
        templates.image_template.format(path="fig4.png") +
        templates.image_template.format(path="fig14.png") +
        templates.table_image_template.format(path="fig5.png") +
        templates.table_image_template.format(path="fig8.png") +
        templates.image_double_template.format(path1="fig5a.png", path2="fig8b.png") +
        templates.image_template.format(path="fig6.png") +
        templates.image_template.format(path="fig10.png") +
        templates.image_template.format(path="fig11.png") +
        templates.tail_template
              )

# write the JSON to the HTML template
with open('result/html_report_plot.html', 'w') as f:
    f.write(html_js_report)

# write image to the HTML template
with open('result/html_report_plot_image.html', 'w') as f:
    f.write(html_image_report)
