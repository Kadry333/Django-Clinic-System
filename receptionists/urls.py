from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.ReceptionistDashboardView.as_view(), name='receptionist_dashboard'),
    path('bookings/',                     views.BookingsView.as_view(),              name='bookings'),
    path('checkin-queue/',                views.CheckInQueueView.as_view(),          name='checkin_queue'),
    path('reschedule/<int:appointment_id>/', views.RescheduleView.as_view(),         name='reschedule'),
    path('schedules/',                    views.SchedulesView.as_view(),             name='schedules'),
    path('schedules/delete/<int:schedule_id>/', views.DeleteScheduleView.as_view(), name='delete_schedule'),
]