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


def find_and_save_repos(base_directory="/Users/natalapuzina/Documents/git_repos"):
    """Scans the given directory for Git repositories and saves them in the database."""

    if not os.path.exists(base_directory):
        print(f"Directory {base_directory} does not exist.")
        return

    repo_paths = []

    # Walk through all subdirectories to find Git repositories
    for root, dirs, files in os.walk(base_directory):
        if ".git" in dirs:  # A Git repository has a ".git" folder
            repo_name = os.path.basename(root)
            repo_path = os.path.abspath(root)

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
