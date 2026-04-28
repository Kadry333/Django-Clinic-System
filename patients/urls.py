from django.urls import path

from patients import views

app_name = "patients"

urlpatterns = [
    # path("book/", views.PatientBookAppointmentView.as_view(), name="book_appointment"),
    # # path("appointments/", views.PatientAppointmentsView.as_view(), name="my_appointments"),
    # # path(
    # #     "appointments/<int:pk>/cancel/",
    # #     views.PatientCancelAppointmentView.as_view(),
    # #     name="cancel_appointment",
    # # ),
    # # path(
    # #     "appointments/<int:pk>/reschedule/",
    # #     views.PatientRescheduleRequestView.as_view(),
    # #     name="reschedule_appointment",
    # # ),
    path(
        "consultation-summary/",
        views.PatientConsultationSummaryView.as_view(),
        name="consultation_summary",
    ),

    path("profile/", views.PatientProfileView.as_view(), name="my_profile"),
    path("profile/edit/", views.PatientProfileUpdateView.as_view(), name="edit_profile"),
    path("admin/", views.AdminPatientsView.as_view(), name="admin_patients"),
    path("admin/<int:pk>/edit/",views.AdminPatientProfileUpdateView.as_view(),name="admin_patient_edit",),
]