import os
import sys
import django


# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

# Now you can import Django models
from report_app.models import Repository


def find_and_save_repos(base_directory=None):
    """Scans the given directory for Git repositories and saves them in the database."""
    if base_directory is None:
        base_directory = os.path.expanduser("~/Documents/git_repos")  # Expands '~' to the home directory

    if not os.path.exists(base_directory):
        print(f"Directory {base_directory} does not exist.")
        return

    repo_paths = []

    print(f"Scanning directory: {base_directory}")

    for folder in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder)
        git_path = os.path.join(folder_path, ".git")

        if os.path.isdir(folder_path) and os.path.isdir(git_path):  # Check if it's a Git repository
            repo_name = folder
            repo_path = os.path.abspath(folder_path)

            # Save to database if not already stored
            repository, created = Repository.objects.get_or_create(
                name=repo_name,
                path=repo_path
            )

            if created:
                print(f"Added to database: {repo_name} -> {repo_path}")
            else:
                print(f"Already exists: {repo_name}")

            repo_paths.append(repo_path)

    if not repo_paths:
        print("No repositories found.")


if __name__ == "__main__":
    find_and_save_repos()
