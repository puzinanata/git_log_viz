import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "./"))
from src import templates
from src import graph
from src import prep_data
from src import collect


def html_report(settings):

    settings["repo_log_csv"] = ["result/git_log_{}.csv".format(repo.split('/')[-1]) for repo in settings["repo_name"]]

    # 1. Data Collection

    # Call function with extracted data in df
    collect.collect_data(
        "result/all_repos_data.csv",
        settings["repo_name"],
        settings["repo_log_csv"]
    )

    # 2. Data Cleaning and Data Processing

    # Call function with cleaned and processed df
    df, last_year_df = prep_data.process_data(
        "result/all_repos_data.csv",
        settings["exclude_username"],
        settings["old_username"],
        settings["new_username"],
        settings["start_year"],
        settings["finish_year"]
    )

    # Call function with data exploration
    # prep_data.explore_data(df)
    # prep_data.explore_data(last_year_df)

    # 3.Data Analysis and Data Visualisation

    # Building line chart with total commits by year.
    fig1_json = graph.graph_line(
        df,
        "year",
        "Count of commits by Year",
        '1'
    )

    # Building line chart with total commits in last year.
    fig4_json = graph.graph_line(
        last_year_df,
        "month_year",
        "Count of commits in last year",
        'M1'
    )

    # Building graph table with top authors by count the commits for all years
    fig2_json = graph.graph_table(
        df,
        'year',
        settings["author"],
        settings["num_top"],
        'commit_count',
        "Total Commits"
    )

    # Building graph table with top authors by count the commits in last year
    fig5_json = graph.graph_table(
        last_year_df,
        'month_year',
        settings["author"],
        settings["num_top"],
        'commit_count',
        "Total Commits"
    )

    # Building graph table with top authors by sum of changes for all years
    fig7_json = graph.graph_table(
        df,
        'year',
        settings["author"],
        settings["num_top"],
        'num_changes',
        "Total Changes (insertions+deletions)"
    )

    # Building graph table with top authors by sum of changes for last year
    fig8_json = graph.graph_table(
        last_year_df,
        'month_year',
        settings["author"],
        settings["num_top"],
        'num_changes',
        "Total Changes (insertions+deletions)"
    )

    # Building bar&line chart by number of authors and commits by year
    fig13_json = graph.graph_bar_line(
        df,
        'year',
        "Number of Authors and Total Commits by Year",
        '1'
    )

    # Building bar&line chart by number of authors and commits in last year
    fig14_json = graph.graph_bar_line(
        last_year_df,
        'month_year',
        "Number of Authors and Total Commits in Last Year",
        'M1'
    )

    # Building pie chart by commit share of top authors for all years
    fig2a_json = graph.graph_pie(
        df,
        'year',
        "Commit Count",
        settings["author"],
        settings["num_top"],
        'commit_count',
        "for All Years"
    )

    # Building pie chart by changes share of top authors for all years
    fig7b_json = graph.graph_pie(
        df,
        'year',
        "Share of Changes",
        settings["author"],
        settings["num_top"],
        'num_changes',
        "for All Years"
    )

    # Building pie chart by commit share of top authors in last year
    fig5a_json = graph.graph_pie(
        last_year_df,
        'month_year',
        "Commit Count",
        settings["author"],
        settings["num_top"],
        'commit_count',
        "in Last Year"
    )

    # Building pie chart by changes share of top authors in last year
    fig8b_json = graph.graph_pie(
        last_year_df,
        'month_year',
        "Share of Changes",
        settings["author"],
        settings["num_top"],
        'num_changes',
        "in Last Year"
    )

    # Building line chart  by top authors by year
    fig3_json = graph.graph_line_author(
        df,
        'year',
        settings["author"],
        settings["num_top"],
        "by Year",
        '1'
    )

    # Building line chart  by top authors in last year
    fig6_json = graph.graph_line_author(
        last_year_df,
        'month_year',
        settings["author"],
        settings["num_top"],
        "in Last Year",
        'M1'
    )

    # Building heatmap graph with distribution commits by hours by top authors for all years
    fig9_json = graph.graph_heatmap(
        df,
        settings["hour"],
        settings["author"],
        settings["num_top"],
        "Top Authors",
        "All Years",
        "top_authors"
    )

    # Building heatmap graph with distribution commits by hours by top authors for last year
    fig10_json = graph.graph_heatmap(
        last_year_df,
        settings["hour"],
        settings["author"],
        settings["num_top"],
        "Top Authors",
        "Last Year",
        "top_authors"
    )

    # Building heatmap graph with distribution commits by hours for all users for all years
    fig12_json = graph.graph_heatmap(
        df,
        settings["hour"],
        settings["author"],
        settings["num_top"],
        "All Users",
        "All Years",
        "all_users"
    )

    # Building heatmap graph with distribution commits by hours for all users for last year
    fig11_json = graph.graph_heatmap(
        last_year_df,
        settings["hour"],
        settings["author"],
        settings["num_top"],
        "All Users",
        "Last Year",
        "all_users"
    )

    fig15_json = graph.graph_bubble(
        df,
        "for All Years"
    )

    fig16_json = graph.graph_bubble(
        last_year_df,
        "in Last Year"
    )

    # Final Section of generation html reports

    # Building of  HTML report with js
    html_js_report = (
            templates.head_js_template +

            # Tab 1 Content
            templates.tab_1_template.format(
                content="\n".join([
                    templates.graph_js_template.format(content=fig1_json, div_name="fig1"),
                    templates.graph_js_template.format(content=fig13_json, div_name="fig13"),
                    templates.table_js_template.format(content=fig2_json, div_name="fig2"),
                    templates.table_js_template.format(content=fig7_json, div_name="fig7"),
                    templates.graph_js_double_template.format(
                        content1=fig2a_json, content2=fig7b_json, div_name1="fig2a", div_name2="fig7b"
                    ),
                    templates.graph_js_template.format(content=fig3_json, div_name="fig3"),
                    templates.graph_js_template.format(content=fig9_json, div_name="fig9"),
                    templates.graph_js_template.format(content=fig12_json, div_name="fig12"),
                ] + (
                    [templates.graph_js_template.format(content=fig15_json, div_name="fig15")]
                    if len(settings["repo_name"]) >= settings["repo_count"] else []
                ))
            ) +

            # Tab 2 Content
            templates.tab_2_template.format(
                content="\n".join([
                    templates.graph_js_template.format(content=fig4_json, div_name="fig4"),
                    templates.graph_js_template.format(content=fig14_json, div_name="fig14"),
                    templates.table_js_template.format(content=fig5_json, div_name="fig5"),
                    templates.table_js_template.format(content=fig8_json, div_name="fig8"),
                    templates.graph_js_double_template.format(
                        content1=fig5a_json, content2=fig8b_json, div_name1="fig5a", div_name2="fig8b"
                    ),
                    templates.graph_js_template.format(content=fig6_json, div_name="fig6"),
                    templates.graph_js_template.format(content=fig10_json, div_name="fig10"),
                    templates.graph_js_template.format(content=fig11_json, div_name="fig11"),
                ] + (
                    [templates.graph_js_template.format(content=fig16_json, div_name="fig16")]
                    if len(settings["repo_name"]) >= settings["repo_count"] else []
                ))
            ) +

            templates.tail_template
    )

    return html_js_report
