# #0. Section: Report settings

# Choose repository: put name of repo
repo_name = [
    './git_repos/neo-go',
    './git_repos/neo',
    './git_repos/neofs-node',
    './git_repos/neofs-sdk-go',
    ]

# Definition of name csv file
#repo_log_csv = "result/git_log_{}.csv".format(repo_name.split('/')[-1])
repo_log_csv = "result/git_log.csv"

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
