from django.urls import path

from . import views

urlpatterns = [
    path("summary/", views.summary_view, name="consultation_summary"),
    path("doctor/", views.doctor_consultation_view, name="consultations"),
]
