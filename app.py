
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Ensure index.html is inside 'templates/' folder

@app.route('/generate_report', methods=['POST'])
def generate_report():
    # Get form data
    repo_list = request.form.get("repo")
    start_year = request.form.get("start_year", 1900)
    finish_year = request.form.get("finish_year", 2025)
    author_type = request.form.get("author", "username")

    # Convert repo list from JSON string to Python list
    repo_list = json.loads(repo_list)

    # Pass user input into settings and trigger your script
    settings = {
        "repo_name": repo_list,
        "start_year": int(start_year),
        "finish_year": int(finish_year),
        "author": author_type
    }

    # Here, you would update your existing settings script to use these values
    # For example, save settings as a JSON file for your script to read
    with open("settings.json", "w") as f:
        json.dump(settings, f)

    # Run the existing script to generate the report
    subprocess.run(["python", "git_log_viz.py"])  # Replace with your actual script

    return redirect(url_for('report'))

@app.route('/report')
def report():
    return render_template('html_report_plot_image.html')  # Ensure report.html is inside 'templates/' folder

if __name__ == '__main__':
    app.run(debug=True)
