import json
import subprocess
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Report
from .models import Repository
from django.conf import settings
import logging
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "./../"))
from scripts import git_log_viz

logger = logging.getLogger(__name__)

def add_repo(request, base_directory="/var/lib/git_repos"):
    """Adds repositories to the database from a list of URLs and ensures they are synced."""
    repo_urls = request.POST.get("repo_urls", "").split(",")
    repo_urls = [url.strip() for url in repo_urls if url.strip()]  # Remove empty values

    logger.debug(f"Received repo URLs: {repo_urls}")  # Log the URLs received

    if not repo_urls:
        return JsonResponse({"error": "No repositories provided."}, status=400)

    # Ensure the base directory exists and is writable
    os.makedirs(base_directory, exist_ok=True)
    if not os.access(base_directory, os.W_OK):
        return JsonResponse({"error": f"Permission denied: {base_directory}"}, status=500)

    added_repos, error_repos = [], []

    for url in repo_urls:
        repo_name = os.path.basename(url).replace(".git", "")
        repo_path = os.path.join(base_directory, repo_name)

        # Check if repository already exists
        repo_exists_in_db = Repository.objects.filter(name=repo_name).exists()
        repo_exists_in_fs = os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, ".git"))

        if repo_exists_in_db and repo_exists_in_fs:
            logger.debug(f"Repo already exists in DB & filesystem: {repo_name}")
            error_repos.append(url)
            continue

        try:
            # Clone the repository
            result = subprocess.run(
                f"cd {base_directory}; git clone {url} 2>&1",
                shell=True, capture_output=True, text=True
            )
            logger.debug(f"Git clone output for {repo_name}: {result.stdout}")
            if result.stderr:
                logger.error(f"Git clone warning/errors: {result.stderr}")

            # Ensure the repository was cloned successfully
            if not os.path.isdir(repo_path) or not os.path.exists(os.path.join(repo_path, ".git")):
                raise RuntimeError(f"Git clone failed: {repo_path} does not exist after cloning.")

            # Add to database
            repo, created = Repository.objects.update_or_create(
                name=repo_name,
                defaults={'path': repo_path, 'url': url}
            )
            if created:
                logger.debug(f"Added new repository: {repo_name}")
            else:
                logger.debug(f"Updated existing repository: {repo_name}")

            added_repos.append(url)

        except Exception as e:
            error_repos.append(url)
            logger.error(f"Error while processing {url}: {str(e)}")

    return JsonResponse({"added": added_repos, "errors": error_repos})


def find_and_sync_repos(base_directory="/var/lib/git_repos"):
    """Scans the given directory for Git repositories and syncs with the database."""
    if not os.path.exists(base_directory):
        print(f"Directory {base_directory} does not exist.")
        return

    current_repo_paths = set()  # Stores repos found in the VM
    print(f"Scanning directory: {base_directory}")

    # Walk through all subdirectories to find Git repositories
    for root, dirs, files in os.walk(base_directory):
        if ".git" in dirs:  # A Git repository has a ".git" folder
            repo_name = os.path.basename(root)
            repo_path = os.path.abspath(root)

            # Save repo paths found on the VM
            current_repo_paths.add(repo_path)

            # Check if repository is already in DB
            repository, created = Repository.objects.get_or_create(
                name=repo_name,
                defaults={'path': repo_path}
            )

            if not created:
                if repository.path != repo_path:
                    repository.path = repo_path  # Update path if different
                    repository.save()
                    print(f"Updated repository path: {repo_name} -> {repo_path}")
                else:
                    print(f"Already exists: {repo_name}")
            else:
                print(f"Added to database: {repo_name} -> {repo_path}")

    # Remove outdated repositories from the database
    for repo in Repository.objects.all():
        if repo.path not in current_repo_paths:
            print(f"Removing outdated repo from database: {repo.name}")
            repo.delete()

    if not current_repo_paths:
        print("No repositories found.")


def index(request):
    find_and_sync_repos()
    repos = Repository.objects.all()  # Fetch repositories after updating the DB
    print("Repositories passed to template:", list(repos))
    return render(request, "report_app/index.html", {"repos": repos})


def save_report(settings, report_content):
    report = Report.objects.create(
        report_name="Git Analytics Report",
        settings_json=settings,
        report_content=git_log_viz.html_report(settings)
    )
    return report


def generate_report(request):
    if request.method == "POST":
        try:
            # Get form data safely
            repo_list = request.POST.getlist("repo")
            repo_count = request.POST.get("repo_count", "1").strip()
            start_year = request.POST.get("start_year", "1900").strip()
            finish_year = request.POST.get("finish_year", "2025").strip()
            author_type = request.POST.get("author", "").strip()
            excl_list = request.POST.get("exclude_username", "").strip()
            old_list = request.POST.get("old_username", "").strip()
            new_list = request.POST.get("new_username", "").strip()
            num_top = request.POST.get("num_top", "10").strip()
            hour_type = request.POST.get("hour", "").strip()

            repo_list = [repo.strip() for repo in repo_list if repo.strip()]

            def parse_list(input_str):
                if input_str:
                    try:
                        return json.loads(input_str) if input_str.startswith("[") else [
                            x.strip() for x in input_str.split(",") if x.strip()
                        ]
                    except json.JSONDecodeError:
                        return [x.strip() for x in input_str.split(",") if x.strip()]
                return []

            excl_list = parse_list(excl_list)
            old_list = parse_list(old_list)
            new_list = parse_list(new_list)

            # Convert numeric values safely
            def safe_int(value, default):
                try:
                    return int(value)
                except ValueError:
                    return default

            repo_count = safe_int(repo_count, 1)
            start_year = safe_int(start_year, 1900)
            finish_year = safe_int(finish_year, 2025)
            num_top = safe_int(num_top, 10)

            # Create settings dictionary
            settings_data = {
                "repo_name": repo_list,
                "repo_count": repo_count,
                "start_year": start_year,
                "finish_year": finish_year,
                "author": author_type,
                "exclude_username": excl_list,
                "old_username": old_list,
                "new_username": new_list,
                "num_top": num_top,
                "hour": hour_type,
            }

            # Ensure result folder exists
            result_dir = os.path.join(settings.BASE_DIR, "result")
            os.makedirs(result_dir, exist_ok=True)

            # Run the script to generate the report
            git_log_viz.html_report(settings_data)

            # Save report metadata in the database
            report_path = os.path.join("report_app", "templates", "report_app", "report.html")
            save_report(settings_data, report_path)

            return redirect("report")

        except Exception as e:
            print("Error in generate_report():", e)
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)


def report(request):
    return render(request, "report_app/report.html")


def update_vm(request):
    # Command to extract data from git log
    command_last_commit = "git log -1 --pretty=format:'%H' --no-merges"

    # Command to update local git repo
    command_pull = "git pull &> /dev/null"

    my_repo_path = subprocess.run(
        'pwd',
        shell=True,
        text=True,
        capture_output=True
    ).stdout.strip()

    my_repo_name = my_repo_path.split('/')[-1]

    last_commit_before_pull = subprocess.run(
        f'cd {my_repo_path}; {command_last_commit}',
        shell=True,
        text=True,
        capture_output=True
    ).stdout.strip()

    message1 = f"Last commit in {my_repo_name} before pulling: {last_commit_before_pull}"

    subprocess.run(
        f'cd {my_repo_path}; {command_pull}',
        shell=True,
        text=True,
        capture_output=True
    ).stdout.strip()

    last_commit_after_pull = subprocess.run(
        f'cd {my_repo_path}; {command_last_commit}',
        shell=True,
        text=True,
        capture_output=True
    ).stdout.strip()

    message2 = f"Last commit in {my_repo_name} after pulling: {last_commit_after_pull}"

    message3 = ""
    message4 = ""
    if last_commit_after_pull != last_commit_before_pull:
        message3 = f"repo {my_repo_name} updated"
    else:
        message4 = f"no changes in repo {my_repo_name}, so it didn't update"

    return JsonResponse({
        "message1": message1,
        "message2": message2,
        "message3": message3,
        "message4": message4,
    })