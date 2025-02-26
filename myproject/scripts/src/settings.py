# #0. Section: Report settings

# Choose repository: put name of repo
repo_name = (
    '$HOME/Documents/git_repos/neo-go',
    '$HOME/Documents/git_repos/neofs-node',
    '$HOME/Documents/git_repos/neofs-sdk-go',
    '$HOME/Documents/git_repos/cpython',
    '$HOME/Documents/git_repos/node',
)
# Define minimal amount of repos for building graph by repos:
repo_count = 5

# Definition of name csv file(-s)
repo_log_csv = []

for repo in repo_name:
    repo_log_csv.append("result/git_log_{}.csv".format(repo.split('/')[-1]))


# Choose Username or Email for author defining
author = 'username'
# author = 'email'

# Username to exclude
exclude_username = []

# Usernames to combine
old_username = []
new_username = []

# Define number of top authors
num_top = 15

# Choose local hour or UTC hour
# hour = 'hour'
hour = 'utc_hour'

# Choose years for report
start_year = 1900
finish_year = 2025
