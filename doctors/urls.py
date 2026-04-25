from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="doctor_dashboard"),

    path("start/<int:queue_id>/", views.start_consultation, name="start_consultation"),
    path("finish/<int:queue_id>/", views.finish_consultation, name="finish_consultation"),
    
    
    path("schedule/", views.schedule_view, name="my_schedule"),
]
