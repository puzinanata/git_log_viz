import unittest
from collect import collect_data


class TestCollectData(unittest.TestCase):
    def test_collect_data_real_repo(self):
        test_repo_path = "/var/lib/git_repos/test"
        test_csv_path = "result/git_log_test.csv"
        output_csv_path = "result/git_log_test_output.csv"

        # Run the actual function
        df = collect_data(
            csv_path=output_csv_path,
            repo_name=[test_repo_path],
            repo_log_csv=[test_csv_path]
        )

        # Assertions
        self.assertFalse(df.empty, "Returned DataFrame should not be empty.")
        self.assertIn("commit", df.columns, "DataFrame should contain 'commit' column.")
        self.assertIn("date", df.columns, "DataFrame should contain 'date' column.")
        self.assertIn("hour", df.columns, "DataFrame should contain 'hour' column.")
        self.assertIn("email", df.columns, "DataFrame should contain 'email' column.")
        self.assertIn("num_changes", df.columns, "DataFrame should contain 'num_changes' column.")


if __name__ == "__main__":
    unittest.main()
