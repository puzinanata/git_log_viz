from . import views


def test_add_repo():
    repo_name = "test_repo"
    views.add_repo(repo_name)