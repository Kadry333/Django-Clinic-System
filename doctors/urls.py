from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="doctor_dashboard"),
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
    path("start/<int:queue_id>/", views.start_consultation, name="start_consultation"),
    path(
        "finish/<int:queue_id>/", views.finish_consultation, name="finish_consultation"
    ),
    path("schedule/", views.DoctorScheduleView.as_view(), name="doctors.schedule"),
    path(
        "schedule/edit/",
        views.DoctorScheduleEditView.as_view(),
        name="doctors.schedule.edit",
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
