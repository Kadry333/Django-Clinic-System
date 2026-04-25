from django.urls import path

from . import views

urlpatterns = [
    path("summary/", views.summary_view, name="consultation_summary"),
    path("doctor/", views.doctor_consultation_view, name="consultations"),
    path("doctor/<int:queue_id>/", views.consultation_form_view, name="consultation_form"),
    path("doctor/<int:queue_id>/submit/", views.consultation_submit_view, name="consultation_submit"),

]
