from django.urls import path

from . import views

urlpatterns = [
    # path("admin-dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("dashboard/", views.AnalyticsDashboardView.as_view(), name="admin_dashboard"),
]
