from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("generate_report", views.generate_report, name="generate_report"),
    path("report", views.report, name="report"),
    path("add_repo/", views.add_repo, name="add_repo"),
    path("update_vm/", views.update_vm, name="update_vm"),
]
