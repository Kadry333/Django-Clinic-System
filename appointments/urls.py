from django.urls import path

from . import views


urlpatterns = [
    path("book/", views.patient_book_view, name="book_appointment"),
    path("book/submit/", views.patient_book_submit, name="book_submit"),
    path(
        "book/cancel/<int:appointment_id>/",
        views.cancel_appointment,
        name="cancel_appointment",
    ),
    path(
        "book/reschedule/request/<int:appointment_id>/",
        views.request_reschedule,
        name="request_reschedule",
    ),
    path("mine/", views.patient_appointments_view, name="my_appointments"),
    path(
        "doctor-management/",
        views.DoctorAppointmentsView.as_view(),
        name="appointments",
    ),
    path(
        "doctor-management/<int:appointment_id>",
        views.DoctorAppointmentView.as_view(),
        name="appointments.appointment",
    ),
    path(
        "doctor-management/<int:appointment_id>/cancel/",
        views.StaffCancelAppointmentView.as_view(),
        name="appointments.cancel",
    ),
    path(
        "doctor-management/<int:appointment_id>/confirm/",
        views.StaffConfirmAppointmentView.as_view(),
        name="appointments.confirm",
    ),
    path(
        "doctor-management/<int:appointment_id>/check_in/",
        views.StaffMarkCheckinAppointmentView.as_view(),
        name="appointments.check_in",
    ),
    path(
        "doctor-management/<int:appointment_id>/complete/",
        views.StaffMarkCompleteAppointmentView.as_view(),
        name="appointments.complete",
    ),
    path(
        "doctor-management/<int:appointment_id>/no_show/",
        views.StaffMarkNoShowAppointmentView.as_view(),
        name="appointments.no_show",
    ),
    path(
        "doctor-management/<int:appointment_id>/confirm-reschedule/",
        views.StaffConfirmRescheduleAppointmentView.as_view(),
        name="appointments.confirm_reschedule",
    ),
    path(
        "doctor-management/<int:appointment_id>/reject-reschedule/",
        views.StaffRejectRescheduleAppointmentView.as_view(),
        name="appointments.reject_reschedule",
    ),
    path(
        "receptionist-bookings/",
        views.receptionist_bookings_view,
        name="receptionist_bookings",
    ),
    path(
        "receptionist-reschedule/",
        views.receptionist_reschedule_view,
        name="receptionist_reschedule",
    ),
]
