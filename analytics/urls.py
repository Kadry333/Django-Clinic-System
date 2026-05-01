from django.urls import path

from . import views

urlpatterns = [
    path("admin-dashboard/", views.AnalyticsDashboardView.as_view(), name="admin_dashboard"),
]
