from django.urls import path

from . import views

urlpatterns = [
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("dashboard/", views.dashboard_view, name="analytics"),
]
