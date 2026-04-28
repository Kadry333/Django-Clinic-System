from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, UpdateView
from accounts.mixins import patientRequiredMixins
from consultations.models import Consultation
from notifications.models import Notification
from notifications.services import create_notification
from patients.forms import PatientProfileForm



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

        create_notification(
            user=self.request.user,
            title="Profile updated",
            notification_type=Notification.NotificationType.PROFILE_UPDATED,
            message="Your profile has been updated successfully.",
        )

        messages.success(self.request, "Your profile has been updated successfully.")
        return response

class PatientConsultationSummaryView(patientRequiredMixins, ListView):
    model = Consultation
    template_name = "patients/consultation_summary.html"
    context_object_name = "consultations"

    def get_queryset(self):
        return (
            Consultation.objects.filter(
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
    

# class PatientBookAppointmentView(patientRequiredMixins, View):
#     form_class = PatientAppointmentBookingForm
#     template_name = "patients/book_appointment.html"
#     success_url = reverse_lazy("patients:my_appointments")

#     def get(self, request, *args, **kwargs):
#         form = self.form_class(data=request.GET or None)

#         if request.GET:
#             form.is_valid()

#         return self.render_booking_page(request, form)

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(data=request.POST, require_slot=True)

#         if form.is_valid():
#             doctor = form.cleaned_data["doctor"]
#             appointment_date = form.cleaned_data["appointment_date"]
#             start_time = form.cleaned_data["slot"]
#             end_time = (
#                 datetime.combine(appointment_date, start_time)
#                 + timedelta(minutes=doctor.session_duration)
#             ).time()

#             try:
#                 with transaction.atomic():
#                     appointment = Appointment.objects.create(
#                         patient=request.user,
#                         doctor=doctor,
#                         appointment_date=appointment_date,
#                         start_time=start_time,
#                         end_time=end_time,
#                         status="requested",
#                     )

#                     patient_name = request.user.get_full_name() or request.user.email
#                     doctor_name = doctor.user.get_full_name() or doctor.user.email

#                     create_notification(
#                         user=request.user,
#                         title="Appointment requested",
#                         notification_type=Notification.NotificationType.APPOINTMENT_REQUESTED,
#                         message="Your appointment request has been submitted successfully.",
#                     )

#                     create_notification(
#                         user=doctor.user,
#                         title="New appointment request",
#                         notification_type=Notification.NotificationType.APPOINTMENT_REQUESTED,
#                         message=(
#                             f"{patient_name} requested an appointment on "
#                             f"{appointment.appointment_date} at {appointment.start_time}."
#                         ),
#                     )

#                     notify_receptionists(
#                         title="New appointment request",
#                         notification_type=Notification.NotificationType.APPOINTMENT_REQUESTED,
#                         message=(
#                             f"{patient_name} requested an appointment with "
#                             f"Dr. {doctor_name} on {appointment.appointment_date} "
#                             f"at {appointment.start_time}."
#                         ),
#                     )

#             except IntegrityError:
#                 form.available_slots = get_available_slots(doctor, appointment_date)
#                 form._set_slot_choices(form.available_slots)
#                 form.add_error(
#                     "slot",
#                     "This slot has just been booked. Please choose another available slot.",
#                 )
#                 return self.render_booking_page(request, form)

#             messages.success(request, "Appointment requested successfully.")
#             return redirect(self.success_url)

#         return self.render_booking_page(request, form)

#     def render_booking_page(self, request, form):
#         availability_checked = (
#             bool(form.data.get("doctor") and form.data.get("appointment_date"))
#             if form.is_bound
#             else False
#         )

#         return render(
#             request,
#             self.template_name,
#             {
#                 "form": form,
#                 "current_role": "Patient",
#                 "availability_checked": availability_checked,
#                 "available_slots": form.available_slots,
#                 "selected_doctor": form.selected_doctor,
#                 "selected_appointment_date": form.selected_appointment_date,
#             },
#         )


# class PatientAppointmentsView(patientRequiredMixins, ListView):
#     model = Appointment
#     template_name = "patients/my_appointments.html"
#     context_object_name = "appointments"

#     def get_queryset(self):
#         return (
#             Appointment.objects.filter(patient=self.request.user)
#             .select_related("doctor", "doctor__user")
#             .order_by("-appointment_date", "-start_time")
#         )

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["current_role"] = "Patient"
#         return context


# class PatientCancelAppointmentView(patientRequiredMixins, View):
#     def post(self, request, pk):
#         appointment = get_object_or_404(
#             Appointment,
#             pk=pk,
#             patient=request.user,
#         )

#         if appointment.status not in ["requested", "confirmed"]:
#             messages.error(request, "You cannot cancel this appointment.")
#             return redirect("patients:my_appointments")

#         appointment.status = "cancelled"
#         appointment.save()

#         patient_name = request.user.get_full_name() or request.user.email
#         doctor_name = appointment.doctor.user.get_full_name() or appointment.doctor.user.email

#         create_notification(
#             user=request.user,
#             title="Appointment cancelled",
#             notification_type=Notification.NotificationType.CANCELLED,
#             message="Your appointment has been cancelled successfully.",
#         )

#         create_notification(
#             user=appointment.doctor.user,
#             title="Appointment cancelled",
#             notification_type=Notification.NotificationType.CANCELLED,
#             message=(
#                 f"{patient_name} cancelled the appointment on "
#                 f"{appointment.appointment_date} at {appointment.start_time}."
#             ),
#         )

#         notify_receptionists(
#             title="Appointment cancelled",
#             notification_type=Notification.NotificationType.CANCELLED,
#             message=(
#                 f"{patient_name} cancelled the appointment with "
#                 f"Dr. {doctor_name} on {appointment.appointment_date} "
#                 f"at {appointment.start_time}."
#             ),
#         )

#         messages.success(request, "Appointment cancelled successfully.")
#         return redirect("patients:my_appointments")


# class PatientRescheduleRequestView(patientRequiredMixins, View):
#     form_class = PatientRescheduleRequestForm
#     template_name = "patients/reschedule_appointment.html"
#     success_url = reverse_lazy("patients:my_appointments")

#     def dispatch(self, request, *args, **kwargs):
#         self.appointment = get_object_or_404(
#             Appointment,
#             pk=kwargs["pk"],
#             patient=request.user,
#         )
#         return super().dispatch(request, *args, **kwargs)

#     def get(self, request, *args, **kwargs):
#         form = self.form_class(
#             data=request.GET or None,
#             appointment=self.appointment,
#         )

#         if request.GET:
#             form.is_valid()

#         return self.render_reschedule_page(request, form)

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(
#             data=request.POST,
#             appointment=self.appointment,
#             require_slot=True,
#         )

#         if form.is_valid():
#             reschedule_request = form.save(commit=False)
#             reschedule_request.appointment = self.appointment
#             reschedule_request.requested_by = self.request.user
#             reschedule_request.status = "pending"
#             reschedule_request.preferred_time = form.cleaned_data["slot"]
#             reschedule_request.save()

#             patient_name = self.request.user.get_full_name() or self.request.user.email
#             doctor_name = (
#                 self.appointment.doctor.user.get_full_name()
#                 or self.appointment.doctor.user.email
#             )

#             create_notification(
#                 user=self.request.user,
#                 title="Reschedule requested",
#                 notification_type=Notification.NotificationType.RESCHEDULED,
#                 message="Your reschedule request has been submitted successfully.",
#             )

#             create_notification(
#                 user=self.appointment.doctor.user,
#                 title="New reschedule request",
#                 notification_type=Notification.NotificationType.RESCHEDULED,
#                 message=(
#                     f"{patient_name} requested to reschedule appointment "
#                     f"#{self.appointment.id} to {reschedule_request.preferred_date} "
#                     f"at {reschedule_request.preferred_time}."
#                 ),
#             )

#             notify_receptionists(
#                 title="New reschedule request",
#                 notification_type=Notification.NotificationType.RESCHEDULED,
#                 message=(
#                     f"{patient_name} requested to reschedule appointment "
#                     f"#{self.appointment.id} with Dr. {doctor_name} "
#                     f"from {self.appointment.appointment_date} at "
#                     f"{self.appointment.start_time} to "
#                     f"{reschedule_request.preferred_date} at "
#                     f"{reschedule_request.preferred_time}."
#                 ),
#             )

#             messages.success(self.request, "Reschedule request submitted successfully.")
#             return redirect(self.success_url)

#         return self.render_reschedule_page(request, form)

#     def render_reschedule_page(self, request, form):
#         availability_checked = (
#             bool(form.data.get("preferred_date")) if form.is_bound else False
#         )

#         return render(
#             request,
#             self.template_name,
#             {
#                 "form": form,
#                 "current_role": "patient",
#                 "appointment": self.appointment,
#                 "availability_checked": availability_checked,
#                 "available_slots": form.available_slots,
#                 "selected_preferred_date": form.selected_preferred_date,
#             },
#         )


