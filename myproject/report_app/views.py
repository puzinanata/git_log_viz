import subprocess
import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from .models import Report
from .models import Repository
from django.contrib.auth.decorators import login_required
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "./../"))
from scripts import git_log_viz
import hashlib
import json


@login_required
def add_repo(request, base_directory="/var/lib/git_repos"):
    """Adds repositories to the database from a list of URLs and ensures they are synced."""
    repo_urls = request.POST.get("repo_urls", "").split(",")
    repo_urls = [url.strip() for url in repo_urls if url.strip()]  # Remove empty values

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
            error_repos.append(url)
            continue

        # Clone the repository
        subprocess.run(
            f"cd {base_directory}; git clone {url} 2>&1",
            shell=True, capture_output=True, text=True
        )

        # Add to database
        Repository.objects.update_or_create(
            name=repo_name,
            defaults={'path': repo_path, 'url': url}
        )
        added_repos.append(url)

    return JsonResponse({"added": added_repos, "errors": error_repos})


def find_and_sync_repos(base_directory="/var/lib/git_repos"):
    """Scans the given directory for Git repositories and syncs with the database."""
    if not os.path.exists(base_directory):
        print(f"Directory {base_directory} does not exist.")
        return

    current_repo_paths = set()  # Stores repos found in the VM

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
    return render(request, "report_app/index.html", {"repos": repos})


def generate_report(request):
    if request.method == "POST":
        # Get form data safely
        repo_list = [repo.strip() for repo in request.POST.getlist("repo") if repo.strip()]
        repo_count = int(request.POST.get("repo_count", 1))
        start_year = int(request.POST.get("start_year", 1900))
        finish_year = int(request.POST.get("finish_year", 2025))
        num_top = int(request.POST.get("num_top", 10))
        author_type = request.POST.get("author", "").strip()
        excl_list = [x.strip() for x in request.POST.get("exclude_username", "").split(",") if
                     x.strip()] if request.POST.get("exclude_username") else []
        old_list = [x.strip() for x in request.POST.get("old_username", "").split(",") if
                    x.strip()] if request.POST.get("old_username") else []
        new_list = [x.strip() for x in request.POST.get("new_username", "").split(",") if
                    x.strip()] if request.POST.get("new_username") else []
        hour_type = request.POST.get("hour", "").strip()

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

        # Calculate the MD5 hash
        json_str = json.dumps(settings_data, sort_keys=True)
        report_name = hashlib.md5(json_str.encode()).hexdigest()

        # Save a new version of report
        new_report = Report.objects.create(
            report_name=report_name,
            settings_json=settings_data,
            report_content=git_log_viz.html_report(settings_data),
        )

        # Find previous saved report with the same hash to display
        previous_report = (
            Report.objects
            .filter(report_name=report_name)
            .exclude(id=new_report.id)
            .order_by('-created_at')
            .first()
        )

        # If a previous report exists, return its content
        if previous_report:
            print("Previous report found — returning cached version")
            # Return the previous report content
            response = JsonResponse({"report_content": previous_report.report_content}, status=200)

            # Now, delete all reports with the same hash, excluding the newly created one
            with transaction.atomic():
                existing_reports = Report.objects.filter(report_name=report_name).exclude(id=new_report.id)
                existing_reports.delete()  # Delete previous reports

        else:
            print("No previous report found — returning newly generated report")
            # Return the newly generated report content
            response = JsonResponse({"report_content": new_report.report_content}, status=200)

    return response


def report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return HttpResponse(report.report_content)


def update_vm(request):
    # Command to extract data from git log
    command_last_commit = "git log -1 --pretty=format:'%H' --no-merges"

    # Command to update local git repo
    command_pull = "git pull &> /dev/null"

    # Command to apply migrations
    command_migrate = "python3 manage.py migrate"

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

    # Apply migrations
    subprocess.run(f'cd {my_repo_path}; {command_migrate}', shell=True)

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
