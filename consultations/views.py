from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from notifications.services import create_notification
from notifications.models import Notification

from appointments.models import AppointmentQueue, Appointment
from consultations.models import Consultation, Prescription, MedicalTest


def consultation_form_view(request, queue_id):
    q = get_object_or_404(AppointmentQueue, id=queue_id)
    # Fetch existing consultation if any
    consultation = Consultation.objects.filter(appointment=q.appointment).first()

    return render(
        request,
        "consultations/doctor_consultation.html",
        {
            "queue": q,
            "consultation": consultation,
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

    consultation, created = Consultation.objects.update_or_create(
        appointment=appointment,
        defaults={
            'diagnosis': diagnosis,
            'notes': notes,
        }
    )

    drugs = request.POST.getlist("drug_name[]")
    doses = request.POST.getlist("dosage[]")
    durations = request.POST.getlist("duration[]")
    instructions = request.POST.getlist("instructions[]")

    consultation.prescription_set.all().delete()

    for name, dose, duration, instr in zip(drugs, doses, durations, instructions):
        if name and name.strip(): 
            Prescription.objects.create(
                consultation=consultation,
                drug_name=name.strip(),
                dosage=dose.strip() if dose else "",
                duration=duration.strip() if duration else "",
                instructions=instr.strip() if instr else "",
            )

    test_names = request.POST.getlist("test_name[]")
    consultation.medicaltest_set.all().delete()

    for t_name in test_names:
        if t_name and t_name.strip():
            MedicalTest.objects.create(
                consultation=consultation, 
                test_name=t_name.strip()
            )

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



