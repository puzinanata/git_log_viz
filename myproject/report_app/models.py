from django.db import models


class Report(models.Model):
    report_name = models.CharField(max_length=255)  # Report name/title
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when report is generated
    settings_json = models.JSONField()  # Stores the settings used for report generation
    file_path = models.CharField(max_length=500, blank=True, null=True)  # Path to the generated report file

    def __str__(self):
        return self.report_name


class Repository(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Repo name
    path = models.CharField(max_length=500, unique=True)  # Repo path
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return self.name
