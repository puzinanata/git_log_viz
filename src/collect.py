import subprocess
import re
import os
import pandas as pd

# 1. Data Collection


def collect_data(
        csv_path: str,
        repo_name: str,
        repo_log_csv: str,):

    # Command to extract data from git log
    command = "git log --pretty=format:'%H %ad %ae' --stat --no-merges"
    command_last_commit = "git log -1 --pretty=format:'%H' --no-merges"
    command_pull = "git pull &> /dev/null"

    # Dictionary to store the log data for each repository
    repo_logs = {}

    # Loop for iteration through repos
    for repo_path, repo_csv in zip(repo_name, repo_log_csv):
        last_commit_id = subprocess.run(
            f"cd {repo_path}; {command_pull}; {command_last_commit}",
            shell=True,
            text=True,
            capture_output=True
        )
        print(f"Last commit in {repo_path} after update:", last_commit_id.stdout)

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
            last_commit_from_csv = ""
            with open(repo_csv, "r") as file:
                lines = file.readlines()
                if len(lines) > 1:
                    last_commit_from_csv = lines[1].strip().split(",")[1]
                    print("Last commit in csv_file before update: ", last_commit_from_csv)
            if last_commit_id.stdout == last_commit_from_csv:
                print(f"No updates in {repo_path}")
            else:
                print("to do algorithm for append new commits to csv")

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

    commits = {}

    # 1.3.Process logs for each repository
    for repo_log, log_csv in zip(repo_logs.items(), repo_log_csv):
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

    # 1.4 Read data from cvs & save df to csv with all repos data
    df = pd.concat([pd.read_csv(file) for file in repo_log_csv], ignore_index=True)
    df.to_csv(csv_path, index=False)

    return df
