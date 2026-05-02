from django.urls import path

from . import views

urlpatterns = [
    path("summary/<int:appointment_id>/", views.summary_view, name="consultation_summary"),
    path("doctor/<int:queue_id>/", views.consultation_form_view, name="consultation_form"),
    path("doctor/<int:queue_id>/submit/", views.consultation_submit_view, name="consultation_submit"),

]
