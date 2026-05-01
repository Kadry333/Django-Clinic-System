from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from notifications.services import create_notification
from notifications.models import Notification

from appointments.models import AppointmentQueue, Appointment
from consultations.models import Consultation, Prescription, MedicalTest


def consultation_form_view(request, queue_id):
    q = get_object_or_404(AppointmentQueue, id=queue_id)

    return render(
        request,
        "consultations/doctor_consultation.html",
        {
            "queue": q,
            "current_role": "Doctor",
        },
    )


def consultation_submit_view(request, queue_id):
    if request.method != "POST":
        return redirect("consultation_form", queue_id=queue_id)

    q = get_object_or_404(AppointmentQueue, id=queue_id)
    appointment = q.appointment

    diagnosis = request.POST.get("diagnosis")
    notes = request.POST.get("notes")

    consultation = Consultation.objects.create(
        appointment=appointment,
        diagnosis=diagnosis,
        notes=notes,
    )

    drugs = request.POST.getlist("drug_name[]")
    doses = request.POST.getlist("dosage[]")
    durations = request.POST.getlist("duration[]")

    for i in range(len(drugs)):
        if drugs[i]:
            Prescription.objects.create(
                consultation=consultation,
                drug_name=drugs[i],
                dosage=doses[i],
                duration=durations[i],
            )

    tests = request.POST.getlist("test_name[]")

    for t in tests:
        if t:
            MedicalTest.objects.create(consultation=consultation, test_name=t)

    q.status = "done"
    q.save()

    appointment.status = "completed"
    appointment.save()

    create_notification(
        user=appointment.patient,
        title="Consultation summary ready",
        notification_type=Notification.NotificationType.CONSULTATION_READY,
        message="Your consultation summary is ready.",
    )

    messages.success(request, "Consultation completed")
    return redirect("doctor_dashboard")


def summary_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    consultation = get_object_or_404(
        Consultation.objects.prefetch_related('prescription_set', 'medicaltest_set'), 
        appointment=appointment
    )

    return render(
        request,
        "consultations/summary.html",
        {
            "current_role": "Patient",
            "appointment": appointment,
            "consultation": consultation,
        },
    )



def doctor_consultation_view(request):
    return render(
        request,
        "consultations/doctor_consultation.html",
        {
            "current_role": "Doctor",
        },
    )
