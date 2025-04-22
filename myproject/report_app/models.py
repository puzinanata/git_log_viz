from django.db import models


class Report(models.Model):
    id = models.AutoField(primary_key=True)
    report_name = models.CharField(max_length=255, blank=True)  # MD5 hash of settings
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when report is generated
    settings_json = models.JSONField()  # Stores the settings used for report generation
    report_content = models.TextField()  # Report HTML content

    def __str__(self):
        return self.report_name


class Repository(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Repo name
    path = models.CharField(max_length=500, unique=True)  # Repo path
    url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates on save

    def __str__(self):
        return self.name


class Commit(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    commit_hash = models.CharField(max_length=40, unique=True)
    date = models.DateTimeField()
    hour = models.IntegerField()
    email = models.EmailField()
    num_changes = models.IntegerField()

    def __str__(self):
        return self.repository.name
