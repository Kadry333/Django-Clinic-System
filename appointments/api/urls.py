from django.urls import path, include
from .routers import router
from .views import (
    available_slots,
    PatientSlotListView,
    PatientAppointmentListCreateView,
    PatientAppointmentCancelView,
    PatientAppointmentRescheduleView,
)

urlpatterns = [
    path('', include(router.urls)),
    path('slots/', available_slots, name='available_slots_api'),


    path('patient/slots/', PatientSlotListView.as_view(), name='patient_slots'),
    path('patient/appointments/', PatientAppointmentListCreateView.as_view(), name='patient_appointments'),
    path('patient/appointments/<int:appointment_id>/cancel/', PatientAppointmentCancelView.as_view(), name='patient_cancel'),
    path('patient/appointments/<int:appointment_id>/reschedule/', PatientAppointmentRescheduleView.as_view(), name='patient_reschedule'),
]