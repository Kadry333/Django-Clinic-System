from django.urls import path

from . import views



urlpatterns = [
    path("book/", views.patient_book_view, name="book_appointment"),
    path("book/submit/", views.patient_book_submit, name="book_submit"),
    path("book/cancel/<int:appointment_id>/", views.cancel_appointment, name="cancel_appointment"),
    path("book/reschedule/request/<int:appointment_id>/", views.request_reschedule, name="request_reschedule"),

    path("mine/", views.patient_appointments_view, name="my_appointments"),
    path("doctor-management/", views.doctor_management_view, name="appointments"),
    path("receptionist-bookings/", views.receptionist_bookings_view, name="receptionist_bookings"),
    path("receptionist-reschedule/", views.receptionist_reschedule_view, name="receptionist_reschedule"),
]