from django.urls import path

from . import views

urlpatterns = [
    path("schedules/", views.schedule_management_view, name="manage_schedules"),
    path("checkin/", views.checkin_view, name="patient_checkin"),
]
