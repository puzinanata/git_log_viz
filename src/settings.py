# #0. Section: Report settings

# Choose repository: put name of repo
repo_name = [
    './git_repos/cpython',
    ]

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
num_top = 10
