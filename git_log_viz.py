import subprocess
import csv
import re
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
from datetime import datetime

# Template section

head_template = """<html>
<head>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
"""
tail_template = """
</body>

</html>"""
graph_template_js = """
    <div id='{div_name}'></div>
    <script>
        var plotly_data = {content}
        Plotly.react('{div_name}', plotly_data.data, plotly_data.layout);
    </script>
"""
table_template_js = """
    <p style="text-align: center; font-size: 18px; font-family: Arial, sans-serif; margin: 30px 0; color:#444">
        Top Authors
    </p>
{}
""".format(graph_template_js)

image_template = """
<img src="{path}" alt="A responsive image" style="max-width: 100%; height: auto;">
"""

# !!!Action required - put path to Bash command
command = "cd ./git_repos/neo-go ; git log "

result = subprocess.run(command, shell=True, text=True, capture_output=True)

# Pattern to extract data
pattern = r"commit\s+([a-f0-9]+)\nAuthor:\s+(.*?)\nDate:\s+(.*)"

matches = re.findall(pattern, result.stdout, re.MULTILINE)

# Write to CSV file
with open("result/git_log.csv", mode="w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["commit", "author", "date"])
    writer.writerows(matches)

df = pd.read_csv('result/git_log.csv')

df["date"] = pd.to_datetime(df["date"], utc=True)
# Creation new columns
df["year"] = df["date"].dt.year
df["year"] = df["year"].astype(int)

df["month_year"] = df["date"].dt.strftime('%Y-%m')
df['month_year'] = pd.to_datetime(df['month_year'], format='%Y-%m')

# Extract emails using regular expression
df["email"] = df["author"].str.extract(r'<([^>]+)>')

# Building line chart #1 by years.

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

# !!!Action required - put number of years instead of 5 if needed
# Building line chart #2 by last X years by month.

# Group by 'month_year' and count the 'commit' occurrences
cutoff_date = pd.to_datetime(f"{datetime.now().year - 5}-01-01")
filtered_df = df[df['month_year'] >= cutoff_date]
monthly_counts = filtered_df.groupby(['month_year'])['commit'].count().reset_index()
monthly_counts.columns = ['month_year', 'commit_count']
fig2 = px.line(monthly_counts, x='month_year', y='commit_count', title='Count of commits by Month', markers=True)

fig2.update_layout(
    title_x=0.5,
    xaxis_tickformat='%Y-%B',
    xaxis=dict(
        tickmode='linear',
        tick0=monthly_counts['month_year'].min(),
        dtick='M1'
    )
)

fig2_json = fig2.to_json()

# Building graph table #3 with top authors

# Grouped by year and email and count the commits
commit_counts = df.groupby(['year', 'email']).size().reset_index(name='commit_count')
total_commits_by_email = commit_counts.groupby('email')['commit_count'].sum()
top_10_emails = total_commits_by_email.sort_values(ascending=False).head(10)

table_data = {
    "Rank": list(range(1, len(top_10_emails) + 1)),
    "Email": top_10_emails.index.tolist(),
    "Total Commits": top_10_emails.values.tolist()
}

fig3 = ff.create_table([list(table_data.keys())] + list(zip(*table_data.values())))

fig3.update_layout(
    title="Top-10 authors",
    title_x=0.5,
)

fig3_json = fig3.to_json()

# Building line chart #4  by top-X authors

# Find the top X emails based on commit count
top_emails = total_commits_by_email.nlargest(10).index

top_commit_counts = commit_counts[commit_counts['email'].isin(top_emails).sort_values(ascending=False)]

fig4 = px.line(
    top_commit_counts,
    x="year",
    y="commit_count",
    color="email",
    title="Count of commits by top authors by years",
    markers=True)

fig4.update_layout(
    legend=dict(
        orientation="h",
        entrywidth=70,
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

fig4_json = fig4.to_json()

# Build HTML report
html_js_report = (
        head_template +
        graph_template_js.format(content=fig1_json, div_name="fig1") +
        graph_template_js.format(content=fig2_json, div_name="fig2") +
        table_template_js.format(content=fig3_json, div_name="fig3") +
        graph_template_js.format(content=fig4_json, div_name="fig4") +
        tail_template
              )

html_image_report = (
        head_template +
        image_template.format(path="fig1.png") +
        tail_template
              )

# write the JSON to the HTML template
with open('result/html_report_plot.html', 'w') as f:
    f.write(html_js_report)

with open('result/html_report_plot_image.html', 'w') as f:
    f.write(html_image_report)
