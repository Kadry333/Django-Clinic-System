from django.shortcuts import render, redirect,get_object_or_404
from datetime import datetime
from doctors.models import DoctorProfile
from patients.models import PatientProfile  

from datetime import datetime, date
from accounts.decorators import patient_required, doctor_required, receptionist_required
from appointments.models import Appointment, RescheduleRequest, AppointmentReschedule
from doctors.models import DoctorProfile
from patients.models import PatientProfile

from .utils import generate_slots
from .services import book_appointment

from django.contrib import messages
from appointments.models import Appointment,RescheduleRequest


from .models import RescheduleRequest

@patient_required
def patient_book_view(request):
    doctors = DoctorProfile.objects.select_related('user').all()
    slots = []
    error = None

    doctor_id = request.GET.get("doctor_id")
    date_str = request.GET.get("date")

    if doctor_id and date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            if selected_date < date.today():
                error = "Invalid date"
            else:
                doctor = DoctorProfile.objects.get(id=doctor_id)
                slots = generate_slots(doctor, selected_date)

        except Exception as e:
            error = str(e)

    return render(
        request,
        "appointments/book.html",
        {
            "current_role": "Patient",
            "doctors": doctors,
            "slots": slots,
            "error": error,
            "today": date.today().isoformat(),
        },
    )

@patient_required
def patient_book_submit(request):
    if request.method != "POST":
        return redirect("book_appointment")

    patient = request.user

    doctor_id = request.POST.get("doctor_id")
    date_str = request.POST.get("date")
    time_str = request.POST.get("time")

    try:
        doctor = DoctorProfile.objects.get(id=doctor_id)
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        selected_time = datetime.strptime(time_str, "%I:%M %p").time()

        if selected_date < date.today():
            raise Exception("Invalid date")

        book_appointment(patient, doctor, selected_date, selected_time)

        messages.success(request, "Appointment booked successfully")
        return redirect("my_appointments")

    except Exception as e:
        doctors = DoctorProfile.objects.all()
        return render(
            request,
            "appointments/book.html",
            {
                "current_role": "Patient",
                "doctors": doctors,
                "error": str(e),
                "slots": [],
                "today": date.today().isoformat(),
            },
        )
@patient_required  
def patient_appointments_view(request):
    patient = request.user

    all_appointments = Appointment.objects.filter(
        patient=patient
    ).select_related('doctor__user').order_by('-appointment_date')

    upcoming = all_appointments.filter(status__in=['requested', 'confirmed', 'checked_in'])
    history  = all_appointments.filter(status__in=['completed', 'cancelled', 'no_show'])

    reschedule_slots = []
    apt_id    = request.GET.get("apt_id")
    doctor_id = request.GET.get("doctor_id")
    date_str  = request.GET.get("date")

    if doctor_id and date_str:
        try:
            doctor = DoctorProfile.objects.get(id=doctor_id)
            date   = datetime.strptime(date_str, "%Y-%m-%d").date()
            reschedule_slots = generate_slots(doctor, date)
        except:
            reschedule_slots = []

    return render(request, "appointments/my_appointments.html", {
        "current_role": "Patient",
        "upcoming": upcoming,
        "history": history,
        "reschedule_slots": reschedule_slots,
        "reschedule_apt_id": apt_id,
        "reschedule_date": date_str,
    })
@patient_required
def cancel_appointment(request, appointment_id):
    patient = request.user

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=patient
    )

    # rule
    if appointment.status not in ['requested', 'confirmed']:
        messages.error(request, "You cannot cancel this appointment.")
        return redirect("my_appointments")

    appointment.status = 'cancelled'
    appointment.save()

    messages.success(request, "Appointment cancelled successfully.")
    return redirect("my_appointments")



@patient_required
def request_reschedule(request, appointment_id):
    patient = request.user

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=patient
    )

    if request.method != "POST":
        return redirect("my_appointments")

    if appointment.status not in ["requested", "confirmed"]:
        messages.error(request, "Cannot request reschedule.")
        return redirect("my_appointments")

    if RescheduleRequest.objects.filter(
        appointment=appointment,
        status="pending"
    ).exists():
        messages.warning(request, "Already requested.")
        return redirect("my_appointments")

    date_str = request.POST.get("date")
    time_str = request.POST.get("time")

    preferred_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    preferred_time = datetime.strptime(time_str, "%I:%M %p").time()

    RescheduleRequest.objects.create(
        appointment=appointment,
        requested_by=patient,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
        reason="Patient requested reschedule"
    )

    messages.success(request, "Request sent.")
    return redirect("my_appointments")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
@doctor_required
def doctor_management_view(request):
    return render(
        request,
        "appointments/doctor_management.html",
        {
            "current_role": "Doctor",
        },
    )

@receptionist_required
def receptionist_bookings_view(request):
    return render(
        request,
        "appointments/receptionist_bookings.html",
        {
            "current_role": "Receptionist",
        },
    )


def receptionist_reschedule_view(request):
    return render(
        request,
        "appointments/receptionist_reschedule.html",
        {
            "current_role": "Receptionist",
        },
    )
