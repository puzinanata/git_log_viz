from django.contrib import admin
from .models import Report


# Register your models here.
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("report_name", "created_at")  # Show timestamp
    ordering = ("-created_at",)  # Sort reports by newest first
