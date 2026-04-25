from django.urls import path

from patients import views

app_name = "patients"

urlpatterns = [
    path("profile/", views.PatientProfileView.as_view(), name="my_profile"),
    path("profile/edit/", views.PatientProfileUpdateView.as_view(), name="edit_profile"),
]