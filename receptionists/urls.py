from django.urls import path
from receptionists import views

urlpatterns = [
    path('', views.ReceptionistDashboardView.as_view(), name='receptionist.dashboard'),
    path('bookings/',views.BookingsView.as_view(),name='bookings'),
    path('checkin-queue/', views.CheckInQueueView.as_view(),name='checkin_queue'),
    path('reschedule/<int:appointment_id>/', views.RescheduleView.as_view(),name='reschedule'),
    path('schedules/',views.SchedulesView.as_view(),name='schedules'),
    path('schedules/edit/<int:schedule_id>/', views.EditScheduleView.as_view(), name='edit.schedule'),
    path('schedules/delete/<int:schedule_id>/', views.DeleteScheduleView.as_view(), name='delete.schedule'),
    path("admin/receptionists/", views.ReceptionistListView.as_view(), name="receptionist.list"),
    path("admin/receptionists/create/", views.ReceptionistCreateView.as_view(), name="receptionist.create"),
    path("admin/receptionists/<int:receptionist_id>/", views.ReceptionistDetailView.as_view(), name="receptionist.detail"),
    path("admin/receptionists/<int:receptionist_id>/edit/", views.ReceptionistEditView.as_view(), name="receptionist.edit"),
    path("admin/receptionists/<int:receptionist_id>/delete/", views.ReceptionistDeleteView.as_view(), name="receptionist.delete"),
    path('reschedule/', views.RescheduleRequestsView.as_view(), name='receptionist.reschedule'),

]

