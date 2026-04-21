from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="doctor_dashboard"),
    path("schedule/", views.schedule_view, name="my_schedule"),
]
