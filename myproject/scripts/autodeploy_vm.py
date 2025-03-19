import subprocess

# Command to extract data from git log
command_last_commit = "git log -1 --pretty=format:'%H' --no-merges"

# Command to update local git repo
command_pull = "git pull &> /dev/null"

my_repo_path = "~/git_log_viz/myproject"
my_repo_name = my_repo_path.split('/')[-1]

last_commit_before_pull = subprocess.run(
            f"sudo bash -c 'cd {my_repo_path}; {command_last_commit}'",
            shell=True,
            text=True,
            capture_output=True
        ).stdout.strip()

print(f"Last commit in {my_repo_name} before pulling:", last_commit_before_pull, flush=True)

# Run sudo git pull (suppress output)
subprocess.run(
    f"sudo bash -c 'cd {my_repo_path}; {command_pull}'",
    shell=True,
    text=True
)

last_commit_after_pull = subprocess.run(
            f"sudo bash -c 'cd {my_repo_path}; {command_last_commit}'",
            shell=True,
            text=True,
            capture_output=True
            ).stdout.strip()

print(f"Last commit in {my_repo_name} after pulling:", last_commit_after_pull, flush=True)

if last_commit_after_pull != last_commit_before_pull:
    print(f"repo {my_repo_name} updated", flush=True)
else:
    print(f"no changes in repo {my_repo_name}, so it didn't update", flush=True)
