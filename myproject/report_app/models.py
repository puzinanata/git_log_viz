from django.db import models
import hashlib
import json


class Report(models.Model):
    id = models.AutoField(primary_key=True)
    report_name = models.CharField(max_length=255, blank=True)  # MD5 hash of settings
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when report is generated
    settings_json = models.JSONField()  # Stores the settings used for report generation
    report_content = models.TextField()  # Report HTML content

    def save(self, *args, **kwargs):
        """Generate MD5 hash from settings_json before saving."""
        json_str = json.dumps(self.settings_json, sort_keys=True)  # Convert JSON to string
        new_hash = hashlib.md5(json_str.encode()).hexdigest()

        self.report_name = new_hash  # Assign the hash as report_name
        super().save(*args, **kwargs)  # Call the parent save method


    def __str__(self):
        return self.report_name


class Repository(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Repo name
    path = models.CharField(max_length=500, unique=True)  # Repo path
    url = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates on save

    def __str__(self):
        return self.name
