from django.urls import path
from doctors.views import (
    DoctorDashboardView,
    StartConsultationView,
    FinishConsultationView,
    ScheduleView,
)
from . import views

urlpatterns = [
    path("dashboard/", DoctorDashboardView.as_view(), name="doctor_dashboard"),
    path("start/<int:queue_id>/", StartConsultationView.as_view(), name="start_consultation"),
    path("finish/<int:queue_id>/", FinishConsultationView.as_view(), name="finish_consultation"),
     
    path("admin/doctors/", views.DoctorsListView.as_view(), name="doctors.list"),
    path(
        "admin/doctors/create/", views.DoctorCreateView.as_view(), name="doctors.create"
    ),
    path(
        "admin/doctors/<int:doctor_id>/",
        views.DoctorDetailView.as_view(),
        name="doctors.detail",
    ),
    path(
        "admin/doctors/<int:doctor_id>/edit/",
        views.DoctorEditView.as_view(),
        name="doctors.edit",
    ),
    path(
        "admin/doctors/<int:doctor_id>/delete/",
        views.DoctorDeleteView.as_view(),
        name="doctors.delete",
    ),
    path("schedule/", views.DoctorScheduleView.as_view(), name="doctors.schedule"),
    path(
        "schedule/create/",
        views.DoctorScheduleCreateView.as_view(),
        name="doctors.schedule.create",
    ),
    path(
        "schedule/edit/<int:schedule_id>/",
        views.DoctorScheduleEditView.as_view(),
        name="doctors.schedule.edit",
    ),
    path(
        "schedule/<int:schedule_id>/delete/",
        views.DoctorScheduleDeleteView.as_view(),
        name="doctors.schedule.delete",
    ),
    path(
        "schedule/exceptions/",
        views.DoctorScheduleExceptionView.as_view(),
        name="doctors.schedule.exceptions",
    ),
    path(
        "schedule/exceptions/new/",
        views.DoctorScheduleExceptionCreateView.as_view(),
        name="doctors.schedule.exceptions.new",
    ),
    path(
        "schedule/exceptions/<int:exception_id>/edit",
        views.DoctorScheduleExceptionEditView.as_view(),
        name="doctors.schedule.exceptions.edit",
    ),
    path(
        "schedule/exceptions/<int:exception_id>/delete/",
        views.DoctorScheduleExceptionDeleteView.as_view(),
        name="doctors.schedule.exceptions.delete",
    ),
    path(
        "schedule/exceptions/<int:exception_id>/",
        views.DoctorScheduleExceptionDetailView.as_view(),
        name="doctors.schedule.exceptions.detail",
    ),
]
