from django.urls import path
from patients import views

app_name = "patients"

urlpatterns = [
    path("consultation-summary/",views.PatientConsultationSummaryView.as_view(),name="consultation.summary"),
    path("profile/",views.PatientProfileView.as_view(),name="profile"),
    path("profile/edit/",views.PatientProfileUpdateView.as_view(),name="profile.edit"),
    path("admin/",views.AdminPatientsView.as_view(),name="admin"),
    path("admin/<int:pk>/", views.AdminPatientDetailView.as_view(), name="admin.patient.detail"),
    path("admin/<int:pk>/edit/",views.AdminPatientProfileUpdateView.as_view(),name="admin.patient.edit"),
    path("admin/<int:pk>/delete/",views.AdminPatientDeleteView.as_view(),name="admin.patient.delete"),
]
