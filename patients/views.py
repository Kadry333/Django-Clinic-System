from datetime import datetime, timedelta

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView, CreateView, ListView

from accounts.mixins import patientRequiredMixins
from patients.forms import (
    PatientProfileForm,
    PatientAppointmentBookingForm,
    PatientRescheduleRequestForm,
)
from notifications.models import Notification
from appointments.models import Appointment, RescheduleRequest
from consultations.models import Consultation


class PatientProfileView(patientRequiredMixins, TemplateView):
    template_name = "patients/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Patient"
        context["patient"] = self.request.user
        return context


class PatientProfileUpdateView(patientRequiredMixins, UpdateView):
    form_class = PatientProfileForm
    template_name = "patients/profile_edit.html"
    success_url = reverse_lazy("patients:my_profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Patient"
        context["patient"] = self.request.user
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        Notification.objects.create(
            user=self.request.user,
            title="Profile updated",
            notification_type=Notification.NotificationType.PROFILE_UPDATED,
            message="Your profile has been updated successfully.",
        )

        messages.success(self.request, "Your profile has been updated successfully.")
        return response


class PatientBookAppointmentView(patientRequiredMixins, CreateView):
    model = Appointment
    form_class = PatientAppointmentBookingForm
    template_name = "patients/book_appointment.html"
    success_url = reverse_lazy("patients:my_appointments")

    def form_valid(self, form):
        appointment = form.save(commit=False)
        appointment.patient = self.request.user
        appointment.status = "requested"

        start_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.start_time,
        )
        appointment.end_time = (
            start_datetime + timedelta(minutes=appointment.doctor.session_duration)
        ).time()

        response = super().form_valid(form)

        Notification.objects.create(
            user=self.request.user,
            title="Appointment requested",
            notification_type=Notification.NotificationType.APPOINTMENT_REQUESTED,
            message="Your appointment request has been submitted successfully.",
        )

        messages.success(self.request, "Appointment requested successfully.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Patient"
        return context


class PatientAppointmentsView(patientRequiredMixins, ListView):
    model = Appointment
    template_name = "patients/my_appointments.html"
    context_object_name = "appointments"

    def get_queryset(self):
        return (
            Appointment.objects
            .filter(patient=self.request.user)
            .select_related("doctor", "doctor__user")
            .order_by("-appointment_date", "-start_time")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Patient"
        return context


class PatientCancelAppointmentView(patientRequiredMixins, View):
    def post(self, request, pk):
        appointment = get_object_or_404(
            Appointment,
            pk=pk,
            patient=request.user,
        )

        if appointment.status not in ["requested", "confirmed"]:
            messages.error(request, "You cannot cancel this appointment.")
            return redirect("patients:my_appointments")

        appointment.status = "cancelled"
        appointment.save()

        Notification.objects.create(
            user=request.user,
            title="Appointment cancelled",
            notification_type=Notification.NotificationType.CANCELLED,
            message="Your appointment has been cancelled successfully.",
        )

        messages.success(request, "Appointment cancelled successfully.")
        return redirect("patients:my_appointments")


class PatientRescheduleRequestView(patientRequiredMixins, CreateView):
    model = RescheduleRequest
    form_class = PatientRescheduleRequestForm
    template_name = "patients/reschedule_appointment.html"
    success_url = reverse_lazy("patients:my_appointments")

    def dispatch(self, request, *args, **kwargs):
        self.appointment = get_object_or_404(
            Appointment,
            pk=kwargs["pk"],
            patient=request.user,
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        reschedule_request = form.save(commit=False)
        reschedule_request.appointment = self.appointment
        reschedule_request.requested_by = self.request.user
        reschedule_request.status = "pending"
        reschedule_request.save()

        Notification.objects.create(
            user=self.request.user,
            title="Reschedule requested",
            notification_type=Notification.NotificationType.RESCHEDULED,
            message="Your reschedule request has been submitted successfully.",
        )

        messages.success(self.request, "Reschedule request submitted successfully.")
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Patient"
        context["appointment"] = self.appointment
        return context


class PatientConsultationSummaryView(patientRequiredMixins, ListView):
    model = Consultation
    template_name = "patients/consultation_summary.html"
    context_object_name = "consultations"

    def get_queryset(self):
        return (
            Consultation.objects
            .filter(
                appointment__patient=self.request.user,
                appointment__status="completed",
            )
            .select_related(
                "appointment",
                "appointment__doctor",
                "appointment__doctor__user",
            )
            .prefetch_related("prescription_set", "medicaltest_set")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Patient"
        return context