from accounts.mixins import (
    patientRequiredMixins,
)

from datetime import date, datetime, timedelta
from http.client import HTTPResponse

from django.contrib import messages
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from appointments.forms import AppointmentRescheduleForm
from appointments.models import Appointment, AppointmentReschedule, RescheduleRequest
from doctors.models import DoctorProfile
from patients.models import PatientProfile

from .services import book_appointment, get_available_slots
from .utils import generate_slots

User = get_user_model()

class PatientBookView(patientRequiredMixins, View):

    def get(self, request):
        doctors = DoctorProfile.objects.select_related("user").all()
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

class PatientBookSubmitView(patientRequiredMixins, View):

    @transaction.atomic
    def post(self, request):
        patient = request.user

        doctor_id = request.POST.get("doctor_id")
        date_str = request.POST.get("date")
        time_str = request.POST.get("time")

        try:
            with transaction.atomic():
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

class PatientAppointmentsView(patientRequiredMixins, View):

    def get(self, request):
        patient = request.user

        all_appointments = (
            Appointment.objects.filter(patient=patient)
            .select_related("doctor__user")
            .order_by("-appointment_date")
        )

        upcoming = all_appointments.filter(
            status__in=["requested", "confirmed", "checked_in"]
        )
        history = all_appointments.filter(
            status__in=["completed", "cancelled", "no_show"]
        )

        reschedule_slots = []
        apt_id = request.GET.get("apt_id")
        doctor_id = request.GET.get("doctor_id")
        date_str = request.GET.get("date")

        if doctor_id and date_str:
            try:
                doctor = DoctorProfile.objects.get(id=doctor_id)
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                reschedule_slots = generate_slots(doctor, selected_date)
            except Exception:
                reschedule_slots = []

        return render(
            request,
            "appointments/my_appointments.html",
            {
                "current_role": "Patient",
                "upcoming": upcoming,
                "history": history,
                "reschedule_slots": reschedule_slots,
                "reschedule_apt_id": apt_id,
                "reschedule_date": date_str,
            },
        )

class CancelAppointmentView(patientRequiredMixins, View):

    def post(self, request, appointment_id):
        patient = request.user

        try:
            with transaction.atomic():
                appointment = get_object_or_404(
                    Appointment, id=appointment_id, patient=patient
                )

                if appointment.status not in ["requested", "confirmed"]:
                    messages.error(request, "You cannot cancel this appointment.")
                    return redirect("my_appointments")

                appointment.status = "cancelled"
                appointment.save()

        except Exception:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect("my_appointments")

        messages.success(request, "Appointment cancelled successfully.")
        return redirect("my_appointments")


class RequestRescheduleView(patientRequiredMixins, View):

    def post(self, request, appointment_id):
        patient = request.user

        try:
            with transaction.atomic():
                appointment = get_object_or_404(
                    Appointment, id=appointment_id, patient=patient
                )

                if appointment.status not in ["requested", "confirmed"]:
                    messages.error(request, "Cannot request reschedule.")
                    return redirect("my_appointments")

                if RescheduleRequest.objects.filter(
                    appointment=appointment, status="pending"
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
                    reason="Patient requested reschedule",
                )

        except Exception:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect("my_appointments")

        messages.success(request, "Request sent.")
        return redirect("my_appointments")


def doctor_management_view(request):
    return render(
        request,
        "appointments/doctor_management.html",
        {
            "current_role": "Doctor",
        },
    )


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


class DoctorAppointmentsView(View):
    sort_map = {
        "doctor": ("doctor__user__first_name", "doctor__user__last_name"),
        "patient": ("patient__first_name", "patient__last_name"),
        "date": ("appointment_date", "start_time"),
        "start_time": ("start_time",),
        "session_duration": ("doctor__session_duration",),
        "status": ("status",),
    }

    def get(self, request):
        doctors = DoctorProfile.objects.select_related("user").order_by(
            "user__first_name"
        )
        patients = User.objects.all().order_by("first_name")

        return render(
            request,
            "appointments/doctor-appointments.html",
            {
                "current_role": "Doctor",
                "status_choices": Appointment.STATUS_CHOICES,
                "doctors": doctors,
                "patients": patients,
            },
        )


class DoctorAppointmentView(View):
    def get(self, request, appointment_id):
        return render(
            request,
            "appointments/doctor-appointment.html",
            {
                "current_role": "Doctor",
                "appointment_id": appointment_id,
            },
        )


class StaffCancelAppointmentView(View):
    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.status not in ["requested", "confirmed"]:
            messages.error(request, "Cannot cancel this appointment.")
            return redirect("appointments")

        appointment.status = "cancelled"
        appointment.save()
        RescheduleRequest.objects.filter(appointment=appointment).delete()
        AppointmentReschedule.objects.filter(appointment=appointment).delete()

        messages.success(request, "Appointment cancelled successfully.")
        return redirect("appointments.appointment", appointment_id=appointment.id)


class StaffConfirmAppointmentView(View):
    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.status != "requested":
            messages.error(request, "Only requested appointments can be confirmed.")
            return redirect("appointments.appointment", appointment_id=appointment.id)

        appointment.status = "confirmed"
        appointment.save()

        messages.success(request, "Appointment confirmed successfully.")
        return redirect("appointments.appointment", appointment_id=appointment.id)


class StaffMarkCheckinAppointmentView(View):
    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.status != "confirmed":
            messages.error(request, "Only confirmed appointments can be checked in.")
            return redirect("appointments.appointment", appointment_id=appointment.id)

        appointment.status = "checked_in"
        appointment.check_in_time = timezone.now()
        appointment.save()

        messages.success(request, "Appointment checked in successfully.")
        return redirect("appointments.appointment", appointment_id=appointment.id)


class StaffMarkCompleteAppointmentView(View):
    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.status != "checked_in":
            messages.error(
                request,
                "Only checked-in appointments can be marked complete.",
            )
            return redirect("appointments.appointment", appointment_id=appointment.id)

        appointment.status = "completed"
        appointment.save()

        messages.success(request, "Appointment marked as completed successfully.")
        return redirect("appointments.appointment", appointment_id=appointment.id)


class StaffMarkNoShowAppointmentView(View):
    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.status != "confirmed":
            messages.error(
                request,
                "Only confirmed appointments can be marked as no-show.",
            )
            return redirect("appointments.appointment", appointment_id=appointment.id)

        appointment.status = "no_show"
        appointment.save()

        messages.success(request, "Appointment marked as no-show successfully.")
        return redirect("appointments.appointment", appointment_id=appointment.id)


class StaffConfirmRescheduleAppointmentView(View):
    def post(self, request, appointment_id):
        appointment = get_object_or_404(
            Appointment.objects.select_related("doctor"),
            id=appointment_id,
        )
        reschedule_request = (
            RescheduleRequest.objects.filter(
                appointment=appointment,
                status="pending",
            )
            .order_by("-created_at")
            .first()
        )

        if not reschedule_request:
            messages.error(request, "No pending reschedule request found.")
            return redirect("appointments.appointment", appointment_id=appointment.id)

        old_date = appointment.appointment_date
        old_time = appointment.start_time
        new_date = reschedule_request.preferred_date
        new_time = reschedule_request.preferred_time

        if not new_date or not new_time:
            messages.error(request, "The reschedule request is missing date or time.")
            return redirect("appointments.appointment", appointment_id=appointment.id)

        end_time = (
            datetime.combine(new_date, new_time)
            + timedelta(minutes=appointment.doctor.session_duration)
        ).time()

        available_slots = get_available_slots(appointment.doctor, new_date)

        new_time_str = new_time.strftime("%I:%M %p")

        if not any(slot["label"].startswith(new_time_str) for slot in available_slots):
            messages.error(
                request,
                "The requested slot is no longer available. Please ask the patient to submit a new reschedule request with an available slot.",
            )
            return redirect("appointments.appointment", appointment_id=appointment.id)
        appointment.appointment_date = new_date
        appointment.start_time = new_time
        appointment.end_time = end_time
        appointment.status = "confirmed"

        try:
            appointment.save()
        except IntegrityError:
            messages.error(
                request,
                "This requested slot is no longer available. Please reschedule to another slot.",
            )
            return redirect("appointments.appointment", appointment_id=appointment.id)

        AppointmentReschedule.objects.create(
            appointment=appointment,
            old_date=old_date,
            old_time=old_time,
            new_date=new_date,
            new_time=new_time,
            changed_by=request.user,
            reason=reschedule_request.reason or "Approved patient reschedule request.",
        )

        reschedule_request.status = "approved"
        reschedule_request.save()

        messages.success(request, "Reschedule request confirmed successfully.")
        return redirect("appointments.appointment", appointment_id=appointment.id)


class StaffRejectRescheduleAppointmentView(View):
    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        reschedule_request = (
            RescheduleRequest.objects.filter(
                appointment=appointment,
                status="pending",
            )
            .order_by("-created_at")
            .first()
        )

        if not reschedule_request:
            messages.error(request, "No pending reschedule request found.")
            return redirect("appointments.appointment", appointment_id=appointment.id)

        reschedule_request.status = "rejected"
        reschedule_request.save()

        if appointment.status == "requested":
            appointment.status = "cancelled"
            appointment.save()
            RescheduleRequest.objects.filter(
                appointment=appointment,
                status="pending",
            ).delete()
            AppointmentReschedule.objects.filter(appointment=appointment).delete()
            messages.success(
                request,
                "Reschedule request rejected and appointment cancelled successfully.",
            )
        elif appointment.status == "confirmed":
            messages.success(request, "Reschedule request rejected successfully.")
        else:
            messages.warning(
                request,
                "Reschedule request rejected, but the appointment status was unchanged.",
            )

        return redirect("appointments.appointment", appointment_id=appointment.id)


class StaffRescheduleAppointmentView(View):
    def get(self, request, appointment_id):
        return render(
            request,
            "appointments/staff-reschedule.html",
            {
                "current_role": "Staff",
                "appointment_id": appointment_id,
            },
        )

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        form = AppointmentRescheduleForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Please correct the errors below.")

        else:
            new_date = form.cleaned_data["new_date"]
            new_time = form.cleaned_data["new_time"]
            reason = form.cleaned_data["reason"]

            end_time = (
                datetime.combine(new_date, new_time)
                + timedelta(minutes=appointment.doctor.session_duration)
            ).time()

            old_time = appointment.start_time
            old_date = appointment.appointment_date
            appointment.appointment_date = new_date
            appointment.start_time = new_time
            appointment.end_time = end_time

            try:
                appointment.save()
            except:
                messages.error(
                    request,
                    "The selected slot is no longer available. Please choose another slot.",
                )
                return redirect(
                    "appointments.appointment", appointment_id=appointment.id
                )

            AppointmentReschedule.objects.create(
                appointment=appointment,
                old_date=old_date,
                old_time=old_time,
                new_date=new_date,
                new_time=new_time,
                changed_by=request.user,
                reason=reason or "Staff rescheduled the appointment.",
            )

            RescheduleRequest.objects.filter(
                appointment=appointment,
                status="pending",
            ).delete()

            return redirect("appointments.appointment", appointment_id=appointment.id)
