from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from appointments.models import AppointmentQueue
from doctors.models import DoctorProfile


def dashboard_view(request):
    doctor = DoctorProfile.objects.first() 
    today = timezone.localtime(timezone.now()).date()


    queue = AppointmentQueue.objects.select_related(
        "appointment__patient"
    ).filter(
        appointment__doctor=doctor,
        appointment__appointment_date=today
    ).order_by("check_in_time")

    return render(
        request,
        "doctors/dashboard.html",
        {
            "current_role": "Doctor",
            "queue": queue,
        },
    )


def start_consultation(request, queue_id):
    q = get_object_or_404(AppointmentQueue, id=queue_id)

    q.status = "in_progress"
    q.save()

    return redirect("doctor_dashboard")


def finish_consultation(request, queue_id):
    return redirect("consultation_form", queue_id=queue_id)

def schedule_view(request):
    return render(
        request,
        "doctors/schedule.html",
        {
            "current_role": "Doctor",
        },
    )
