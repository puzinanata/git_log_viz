from django.contrib import admin
from .models import Report
from .models import Repository


# Register your models here.
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "report_name", "created_at")  # Show timestamp
    readonly_fields = ("report_name",)  # Prevent automatic editing
    ordering = ("-created_at",)  # Sort reports by newest first


@admin.register(Repository)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("name", "path", "url","created_at", "updated_at")  # Show in list view
    list_filter = ("created_at", "updated_at")  # Filters for easier navigation
    ordering = ("-updated_at",)  # Sort by most recently updated
    readonly_fields = ("created_at", "updated_at")  # Prevent manual edits
