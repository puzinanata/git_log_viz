import json
import subprocess
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from report_app.models import Report, Repository
from django.conf import settings


def find_and_save_repos(base_directory=None):
    """Scans the given directory for Git repositories and saves them in the database."""
    if base_directory is None:
        base_directory = os.path.expanduser("~/Documents/git_repos")  # Expands '~' to the home directory

    if not os.path.exists(base_directory):
        print(f"Directory {base_directory} does not exist.")
        return

    repo_paths = []
    print(f"Scanning directory: {base_directory}")

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


def index(request):
    find_and_save_repos()  # Run the function before fetching repos
    repos = Repository.objects.all()  # Fetch repositories after updating the DB
    print("Repositories passed to template:", list(repos))
    return render(request, "report_app/index.html", {"repos": repos})


def save_report(settings, file_path):
    """Save report metadata to the database."""
    report = Report.objects.create(
        report_name="Git Analytics Report",
        settings_json=settings,
        file_path=file_path
    )
    return report


def generate_report(request):
    if request.method == "POST":
        try:
            # Get form data safely
            repo_list = request.POST.getlist("repo")
            repo_count = request.POST.get("repo_count", "0").strip()
            start_year = request.POST.get("start_year", "1900").strip()
            finish_year = request.POST.get("finish_year", "2024").strip()
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

            repo_count = safe_int(repo_count, 0)
            start_year = safe_int(start_year, 1900)
            finish_year = safe_int(finish_year, 2024)
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

            # Save settings to JSON file
            settings_path = os.path.join(result_dir, "settings.json")
            with open(settings_path, "w") as f:
                json.dump(settings_data, f, indent=4)

            # Run the script to generate the report
            try:
                subprocess.run(["python", "scripts/git_log_viz.py"], check=True)
            except subprocess.CalledProcessError as e:
                return JsonResponse({"error": f"Script execution failed: {e}"}, status=500)

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
