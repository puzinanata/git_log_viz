from flask import Flask, render_template, request, redirect, url_for
import json
import subprocess

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        # Get form data with default values if missing
        repo_list = request.form.get("repo", "").strip()
        repo_count = request.form.get("repo_count", "0").strip()
        start_year = request.form.get("start_year", "1900").strip()
        finish_year = request.form.get("finish_year", "2024").strip()
        author_type = request.form.get("author", "").strip()
        excl_list = request.form.get("exclude_username", "").strip()
        old_list = request.form.get("old_username", "").strip()
        new_list = request.form.get("new_username", "").strip()
        num_top = request.form.get("num_top", "10").strip()
        hour_type = request.form.get("hour", "").strip()

        # Convert repo_list safely (JSON format or comma-separated list)
        if repo_list:
            try:
                repo_list = json.loads(repo_list) if repo_list.startswith("[") else repo_list.split(",")
            except json.JSONDecodeError:
                repo_list = repo_list.split(",")
        repo_list = [repo.strip() for repo in repo_list if repo.strip()]  # Clean spaces

        # Convert username lists safely (JSON format or comma-separated)
        def parse_list(input_str):
            """Helper function to parse JSON or comma-separated lists."""
            if input_str:
                try:
                    return json.loads(input_str) if input_str.startswith("[") else [x.strip() for x in
                                                                                    input_str.split(",") if x.strip()]
                except json.JSONDecodeError:
                    return [x.strip() for x in input_str.split(",") if x.strip()]
            return []

        excl_list = parse_list(excl_list)
        old_list = parse_list(old_list)
        new_list = parse_list(new_list)

        # Convert numeric values safely
        try:
            repo_count = int(repo_count)
        except ValueError:
            repo_count = 0

        try:
            start_year = int(start_year)
        except ValueError:
            start_year = 1900

        try:
            finish_year = int(finish_year)
        except ValueError:
            finish_year = 2024

        try:
            num_top = int(num_top)
        except ValueError:
            num_top = 10

        # Create settings dictionary
        settings = {
            "repo_name": repo_list,
            "repo_count": repo_count,
            "start_year": start_year,
            "finish_year": finish_year,
            "author": author_type,
            "exclude_username": excl_list,
            "old_username": old_list,
            "new_username": new_list,
            "num_top": num_top,
            "hour": hour_type
        }

        # Save settings to JSON file
        with open("result/settings.json", "w") as f:
            json.dump(settings, f, indent=4)

        # Run the script to generate the report
        subprocess.run(["python", "git_log_viz.py"], check=True)

        return redirect(url_for('report'))

    except Exception as e:
        print("Error in generate_report():", e)
        return "An error occurred while generating the report.", 500


@app.route('/report')
def report():
    return render_template('report.html')


if __name__ == '__main__':
    app.run(debug=True)
