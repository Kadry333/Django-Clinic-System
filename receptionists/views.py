from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages

from appointments.models import Appointment, AppointmentQueue


def schedule_management_view(request):
    return render(
        request,
        "receptionists/schedule_management.html",
        {
            "current_role": "Receptionist",
        },
    )



def checkin_view(request):

    today = timezone.localtime(timezone.now()).date()



    appointments = Appointment.objects.select_related(
        "patient", "doctor__user"
    ).filter(
        appointment_date=today
    ).order_by("start_time")

    queue = AppointmentQueue.objects.select_related(
        "appointment__patient"
    ).filter(
        appointment__appointment_date=today
    ).order_by("check_in_time")

    return render(
        request,
        "receptionists/checkin.html",
        {
            "current_role": "Receptionist",
            "appointments": appointments,
            "queue": queue,
        },
    )


def check_in_patient(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "confirmed":
        messages.error(request, "Cannot check-in this appointment")
        return redirect("patient_checkin")

    if hasattr(appointment, "appointmentqueue"):
        messages.warning(request, "Already checked-in")
        return redirect("patient_checkin")

    appointment.status = "checked_in"
    appointment.check_in_time = timezone.now()
    appointment.save()

    AppointmentQueue.objects.create(
        appointment=appointment,
        check_in_time=appointment.check_in_time
    )

    messages.success(request, "Patient checked-in successfully")
    return redirect("patient_checkin")