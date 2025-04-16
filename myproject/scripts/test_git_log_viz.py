from . import git_log_viz
import hashlib
import os


def test_csv():
    # Preparation
    result_file_csv = "result/git_log_test.csv"
    if os.path.exists(result_file_csv):
        os.remove(result_file_csv)
        print(f"{result_file_csv} has been removed.")

    # Test
    expected_report_md5sum= "999e998e8667232e45356a91c671a036"
    settings_json = {"repo_name": ["/var/lib/git_repos/test"],
                     "repo_count": 1,
                     "start_year": 2000,
                     "finish_year": 2025,
                     "author": "username",
                     "exclude_username": [],
                     "old_username": [],
                     "new_username": [],
                     "num_top": 10,
                     "hour": "hour",
                     "repo_log_csv": [result_file_csv]}
    git_log_viz.html_report(settings_json)

    actual_report_md5sum = md5sum(result_file_csv)

    assert actual_report_md5sum == expected_report_md5sum



def md5sum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
