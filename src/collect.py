import subprocess
import re
import os
import pandas as pd

# 1. Data Collection


def collect_data(
        csv_path: str,
        repo_name: list,
        repo_log_csv: list):

    # Command to extract data from git log
    command = "git log --pretty=format:'%H %ad %ae' --stat --no-merges"
    command_last_commit = "git log -1 --pretty=format:'%H' --no-merges"
    # Command to update local git repo
    command_pull = "git pull &> /dev/null"

    # Dictionary to store the log data for each repository
    repo_logs = {}  # dict to keep full repo
    repo_logs_upd = {}  # dict to keep only new commits after pulling

    # Loop for iteration through repos
    for repo_path, repo_csv in zip(repo_name, repo_log_csv):
        last_commit_before_pull = subprocess.run(
            f"cd {repo_path}; {command_last_commit}",
            shell=True,
            text=True,
            capture_output=True
        ).stdout.strip()

        print(f"Last commit in {repo_path} before pulling:", last_commit_before_pull)

        last_commit_after_pull = subprocess.run(
            f"cd {repo_path}; {command_pull}; {command_last_commit}",
            shell=True,
            text=True,
            capture_output=True
        ).stdout.strip()

        print(f"Last commit in {repo_path} after pulling:", last_commit_after_pull)

        if not os.path.exists(repo_csv):
            print(f"DB csv file '{repo_csv}' doesn't exist.")
            result = subprocess.run(
                f"cd {repo_path}; {command}",
                shell=True,
                text=True,
                capture_output=True
            ).stdout
            repo_logs[repo_path] = result

        else:
            print(f"DB csv file '{repo_csv}' exists so checking new commits...")

            last_commit_from_csv = ""
            df_existing = pd.read_csv(repo_csv) if os.path.exists(repo_csv) else pd.DataFrame()

            if not df_existing.empty:
                last_commit_from_csv = df_existing.iloc[0]['commit']
                print(f"Last commit in CSV before update: {last_commit_from_csv}")

            if last_commit_after_pull == last_commit_from_csv:
                print(f"No updates in {repo_path}")
            else:
                command_new_commits = (f"git log "
                                       f"{last_commit_from_csv}"
                                       f"..HEAD --pretty=format:'%H %ad %ae' --stat --no-merges"
                                       )
                count_new_commits = f"git rev-list --count {last_commit_from_csv}..HEAD --no-merges"

                new_commits = subprocess.run(
                    f"cd {repo_path}; {command_new_commits}",
                    shell=True,
                    text=True,
                    capture_output=True
                ).stdout.strip()

                count_commit = subprocess.run(
                    f"cd {repo_path}; {count_new_commits}",
                    shell=True,
                    text=True,
                    capture_output=True
                ).stdout.strip()

                if int(count_commit) == 0:
                    print(f"No commits will be added to {repo_path}")
                else:
                    print(f"{count_commit} new commits in {repo_path} should be added after update to csv")
                    repo_logs_upd[repo_path] = new_commits

    # 1.2. Process the output

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

    # 1.3.Process logs for each repository
    def process_log(dict_name: dict, create_db: bool):
        commits = {}

        for repo_log in dict_name.items():
            log_data = repo_log[1]
            repo = repo_log[0]
            log_csv = "result/git_log_{}.csv".format(repo.split('/')[-1])
            lines = log_data.splitlines()
            commits[repo] = []

            for line in lines:
                commit_match = re.match(commit_pattern, line)
                summary_match = re.search(summary_pattern, line)

                if commit_match:
                    timestamp = commit_match.group(2)
                    hour_match = re.search(hour_pattern, timestamp)

                    commits[repo].append({
                        "repo": repo,
                        "commit": commit_match.group(1),
                        "date": commit_match.group(2),
                        "hour": int(hour_match.group(1)) if hour_match else 0,
                        "email": commit_match.group(3),
                        "num_changes": 0,
                    })
                elif summary_match and commits[repo]:
                    num_insertions = int(summary_match.group(2)) if summary_match.group(2) else 0
                    num_deletions = int(summary_match.group(3)) if summary_match.group(3) else 0
                    commits[repo][-1]["num_changes"] = num_insertions + num_deletions
            if create_db:
                pd.DataFrame(commits[repo]).to_csv(log_csv, index=False)
            else:
                df_combined = pd.concat(
                    [pd.DataFrame(commits[repo]),
                     pd.read_csv(log_csv)], ignore_index=True).drop_duplicates(subset=["commit"])
                df_combined.to_csv(log_csv, index=False)

    # create new DB
    process_log(repo_logs, True)
    # update exist
    process_log(repo_logs_upd, False)

    # 1.4 Read data from cvs & save df to csv with all repos data
    df = pd.concat([pd.read_csv(file) for file in repo_log_csv], ignore_index=True)
    df.to_csv(csv_path, index=False)
    return df
