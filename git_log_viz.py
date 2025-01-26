import subprocess
import re
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
from datetime import datetime, timedelta
# #0. Section: Report settings

# Choose repository: put name of repo
repo_name = 'neo-go'

# Choose Username or Email for author defining
author = 'username'
# author = 'email'

# Username to exclude
exclude_username = []

# Usernames to combine
old_username = []
new_username = []

# Define number of top authors
num_top = 10

# #1. Template section

head_js_template = """<html>
<head>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
"""
head_template = """<html>
<head>
    
</head>
<body>
"""

tail_template = """
</body>

</html>"""
graph_js_template = """
    <div id='{div_name}'></div>
    <script>
        var plotly_data = {content}
        Plotly.react('{div_name}', plotly_data.data, plotly_data.layout);
    </script>
"""
table_js_template = """
    <p style="text-align: center; font-size: 18px; font-family: Arial, sans-serif; margin: 30px 0; color:#444">
        Top Authors
    </p>
{}
""".format(graph_js_template)

image_template = """
<img src="{path}" style="max-width: 100%; height: auto;">
"""

table_image_template = """
    <p style="text-align: center; font-size: 18px; font-family: Arial, sans-serif; margin: 30px 0; color:#444">
        Top Authors
    </p>
{}
""".format(image_template)

# #2. Section: CSV file generation from git logs

# Step 1: Command to extract data from git log

command = ("cd ./git_repos/{} ; git log --pretty=format:'%H %ae %ad' --date=short --stat --no-merges").format(repo_name)
result = subprocess.run(command, shell=True, text=True, capture_output=True)

# Step 2: Process the output
lines = result.stdout.splitlines()
commits = []

# Regex to match commit details and the summary line
commit_pattern = r"^([a-f0-9]{40})\s+(\S+)\s+(.+)"

#  summary_pattern covers following cases:
#  2 files changed, 0 insertions(+), 0 deletions(-)
#  2 files changed, 0 insertions(+)
#  2 files changed, 0 deletions(-)
#  2 file changed, 0 insertions(+), 0 deletions(-)
#  2 file changed, 0 insertions(+)
#  2 file changed, 0 deletions(-)
summary_pattern = r"(\d+) files? \S+, (\d+) \S+?\([\+\-]\),? ?(\d+)?"


# Parse the lines
for line in lines:
    commit_match = re.match(commit_pattern, line)
    summary_match = re.search(summary_pattern, line)

    if commit_match:
        # Start a new commit entry
        commits.append({
            "commit": commit_match.group(1),
            "email": commit_match.group(2),
            "date": commit_match.group(3),
            "num_changes": 0,  # Placeholder for total changes
        })
    elif summary_match:
        if summary_match.lastindex == 3:
            # Update the last commit with summary data
            num_insertions = int(summary_match.group(2))
            num_deletions = int(summary_match.group(3))
            commits[-1]["num_changes"] = num_insertions + num_deletions
        elif summary_match.lastindex == 2:
            commits[-1]["num_changes"] = int(summary_match.group(2))
        else:
            exit(1)


# Step 3: Convert to a DataFrame
df = pd.DataFrame(commits)

# Step 4: Save to CSV
df.to_csv("result/git_log_with_changes.csv", index=False)

# #3. Section of data preparation
df = pd.read_csv('result/git_log_with_changes.csv')

df["date"] = pd.to_datetime(df["date"], utc=True)
# Creation new columns
df["year"] = df["date"].dt.year
df["year"] = df["year"].astype(int)

df["month_year"] = df["date"].dt.strftime('%Y-%m')
df['month_year'] = pd.to_datetime(df['month_year'], format='%Y-%m')


# Extract the part before '@' to create new column 'Username'
df['username'] = df['email'].str.split('@').str[0]

# Exclude the username
df = df[~df['username'].isin(exclude_username)]

# Replace all occurrences of old username with new username
df['username'] = df['username'].replace(old_username, new_username)

# Transfer username to lower case
df['username'] = df['username'].str.lower()

# #4. Section of graphs building

# Building line chart with commits by years.

# Group by 'year' and count the 'commit' occurrences
yearly_counts = df.groupby('year')['commit'].count().reset_index()
yearly_counts.columns = ['year', 'commit_count']
fig1 = px.line(yearly_counts, x='year', y='commit_count', title='Count of commits by Year', markers=True)

fig1.update_layout(
    title_x=0.5,
    xaxis=dict(
        tickmode='linear',  # Ensure linear ticks (e.g., 2018, 2019, ...)
        tick0=yearly_counts['year'].min(),  # Start ticks from the minimum year
        dtick=1  # Interval between ticks
    )
)

fig1.write_image("result/fig1.png", width=1424, height=450, scale=2)
fig1_json = fig1.to_json()


# Building graph table with top authors

# Grouped by year and email and count the commits
commit_counts = df.groupby(['year', author]).size().reset_index(name='commit_count')
total_commits_by_email = commit_counts.groupby(author)['commit_count'].sum()
top_x_emails = total_commits_by_email.sort_values(ascending=False).head(num_top)

table_data = {
    "Rank": list(range(1, len(top_x_emails) + 1)),
    "Author": top_x_emails.index.tolist(),
    "Total Commits": top_x_emails.values.tolist()
}

fig2 = ff.create_table([list(table_data.keys())] + list(zip(*table_data.values())))

fig2.write_image("result/fig2.png", width=1424, height=450, scale=2)
fig2_json = fig2.to_json()

# Building line chart  by top authors

# Find the top X emails based on commit count
top_emails = total_commits_by_email.nlargest(num_top).index

top_commit_counts = commit_counts[commit_counts[author].isin(top_emails).sort_values(ascending=False)]

fig3 = px.line(
    top_commit_counts,
    x="year",
    y="commit_count",
    color=author,
    title="Count of commits by top authors by years",
    markers=True)

fig3.update_layout(
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
        tick0=yearly_counts['year'].min(),
        dtick=1
    )
)

fig3.write_image("result/fig3.png", width=1409, height=450, scale=2)
fig3_json = fig3.to_json()


# Building line chart by last 12 months before current date

# Group by 'month_year' and count the 'commit' occurrences
cutoff_date = datetime.now() - timedelta(days=365)
filtered_df = df[df['month_year'] >= cutoff_date]
monthly_counts = filtered_df.groupby(['month_year'])['commit'].count().reset_index()
monthly_counts.columns = ['month_year', 'commit_count']
fig4 = px.line(
    monthly_counts,
    x='month_year',
    y='commit_count',
    title='Count of commits by last 12 months',
    markers=True
)

fig4.update_layout(
    title_x=0.5,
    xaxis_tickformat='%Y-%B',
    xaxis=dict(
        tickmode='linear',
        tick0=monthly_counts['month_year'].min(),
        dtick='M1'
    )
)

fig4.write_image("result/fig4.png", width=1424, height=450, scale=2)
fig4_json = fig4.to_json()

# Building graph table with top authors by last 12 months

# Grouped by year and email and count the commits
commit_counts = filtered_df.groupby(['month_year', author]).size().reset_index(name='commit_count')
total_commits_by_email = commit_counts.groupby(author)['commit_count'].sum()
top_x_emails = total_commits_by_email.sort_values(ascending=False).head(num_top)

table_data = {
    "Rank": list(range(1, len(top_x_emails) + 1)),
    "Author": top_x_emails.index.tolist(),
    "Total Commits": top_x_emails.values.tolist()
}

fig5 = ff.create_table([list(table_data.keys())] + list(zip(*table_data.values())))

fig5.write_image("result/fig5.png", width=1424, height=450, scale=2)
fig5_json = fig5.to_json()

# Building line chart  by top authors

# Find the top X emails based on commit count
top_emails = total_commits_by_email.nlargest(num_top).index

top_commit_counts = commit_counts[commit_counts[author].isin(top_emails).sort_values(ascending=False)]

fig6 = px.line(
    top_commit_counts,
    x="month_year",
    y="commit_count",
    color=author,
    title="Count of commits by top authors by last 12 months",
    markers=True)

fig6.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    title_x=0.5,
    xaxis_tickformat='%Y-%B',
    xaxis=dict(
        tickmode='linear',
        tick0=monthly_counts['month_year'].min(),
        dtick='M1'
    )
)

fig6.write_image("result/fig6.png", width=1409, height=450, scale=2)
fig6_json = fig6.to_json()

# #5. Final Section of generation html reports

# Building of  HTML report with js
html_js_report = (
        head_js_template +
        graph_js_template.format(content=fig1_json, div_name="fig1") +
        table_js_template.format(content=fig2_json, div_name="fig2") +
        graph_js_template.format(content=fig3_json, div_name="fig3") +
        graph_js_template.format(content=fig4_json, div_name="fig4") +
        table_js_template.format(content=fig5_json, div_name="fig5") +
        graph_js_template.format(content=fig6_json, div_name="fig6") +
        tail_template
              )

# Building of  HTML report with static images
html_image_report = (
        head_template +
        image_template.format(path="fig1.png") +
        table_image_template.format(path="fig2.png") +
        image_template.format(path="fig3.png") +
        image_template.format(path="fig4.png") +
        table_image_template.format(path="fig5.png") +
        image_template.format(path="fig6.png") +
        tail_template
              )

# write the JSON to the HTML template
with open('result/html_report_plot.html', 'w') as f:
    f.write(html_js_report)

# write image to the HTML template
with open('result/html_report_plot_image.html', 'w') as f:
    f.write(html_image_report)
