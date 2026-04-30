from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction

from accounts.mixins import ReceptionistRequiredMixins
from appointments.models import Appointment, AppointmentReschedule, AppointmentQueue
from doctors.models import DoctorProfile, DoctorSchedule, DoctorScheduleException
from .forms import RescheduleForm, DoctorScheduleForm, DoctorScheduleExceptionForm
from datetime import datetime, timedelta
from django.db import IntegrityError, transaction
from appointments.services import get_available_slots
from django.db.models import Q
from notifications.services import create_notification
from notifications.models import Notification

User = get_user_model()



class ReceptionistDashboardView(ReceptionistRequiredMixins, View):
    def get(self, request):
        today = datetime.now().date()
        context = {
            'total_today':     Appointment.objects.filter(appointment_date=today).count(),
            'confirmed_today': Appointment.objects.filter(appointment_date=today, status='confirmed').count(),
            'checked_in':      Appointment.objects.filter(appointment_date=today, status='checked_in').count(),
            'requested':       Appointment.objects.filter(status='requested').count(),
        }
        return render(request, 'receptionists/dashboard.html', context)


class BookingsView(ReceptionistRequiredMixins, View):
    def get(self, request):
        status = request.GET.get("status", "")
        date_from = request.GET.get("date_from", "")
        date_to = request.GET.get("date_to", "")
        doctor_id = request.GET.get("doctor", "")
        patient_id = request.GET.get("patient", "")
        search = request.GET.get("search", "")

        appointments = Appointment.objects.select_related(
            "patient",
            "doctor__user",
        ).all()

        if status:
            appointments = appointments.filter(status=status)

        if date_from:
            appointments = appointments.filter(appointment_date__gte=date_from)

        if date_to:
            appointments = appointments.filter(appointment_date__lte=date_to)

        if doctor_id:
            appointments = appointments.filter(doctor_id=doctor_id)

        if patient_id:
            appointments = appointments.filter(patient_id=patient_id)

        if search:
            search_filter = (
                Q(patient__first_name__icontains=search)
                | Q(patient__last_name__icontains=search)
            )

            if search.isdigit():
                search_filter |= Q(patient_id=int(search))

            appointments = appointments.filter(search_filter)

        reschedule_appointment = None
        reschedule_slots = []
        reschedule_apt_id = request.GET.get("apt_id")
        reschedule_date = request.GET.get("date")

        if reschedule_apt_id:
            reschedule_appointment = get_object_or_404(
                Appointment.objects.select_related("patient", "doctor__user"),
                id=reschedule_apt_id,
            )

        if reschedule_appointment and reschedule_date:
            try:
                selected_date = datetime.strptime(reschedule_date, "%Y-%m-%d").date()
                reschedule_slots = get_available_slots(
                    reschedule_appointment.doctor,
                    selected_date,
                )
            except Exception:
                reschedule_slots = []

        appointments = appointments.order_by("-appointment_date", "-start_time")

        paginator = Paginator(appointments, 10)
        current_page = paginator.get_page(request.GET.get("page", 1))

        context = {
            "appointments": current_page,
            "page_obj": current_page,
            "status_choices": Appointment.STATUS_CHOICES,
            "doctors": DoctorProfile.objects.select_related("user").all(),
            "patients": User.objects.filter(groups__name="patient").distinct(),
            "reschedule_appointment": reschedule_appointment,
            "reschedule_slots": reschedule_slots,
            "reschedule_date": reschedule_date,
        }

        return render(request, "receptionists/bookings.html", context)

    def post(self, request):
        appointment_id = request.POST.get("appointment_id")
        action = request.POST.get("action")

        try:
            with transaction.atomic():
                appointment = get_object_or_404(Appointment, id=appointment_id)
                status = appointment.status.lower()

                if action == "confirm":
                    if status == "requested":
                        appointment.status = "confirmed"
                        appointment.save()
                        messages.success(request, "Appointment confirmed.")
                    else:
                        messages.error(
                            request,
                            "Only requested appointments can be confirmed.",
                        )

                elif action == "cancel":
                    if status in ["requested", "confirmed"]:
                        appointment.status = "cancelled"
                        appointment.save()
                        messages.success(request, "Appointment cancelled.")
                        create_notification(
                           user=appointment.patient,
                           title="Appointment Cancelled",
                           message=(f"Your appointment on with Dr {appointment.doctor.user.get_full_name()} on {appointment.appointment_date} at {appointment.start_time} has been cancelled. "),
                    
                          notification_type=Notification.NotificationType.RESCHEDULED,
                     )
                    else:
                        messages.error(request, "This appointment cannot be cancelled.")

        except Exception:
            messages.error(request, "Something went wrong. Please try again.")

        return redirect("bookings")



class CheckInQueueView(ReceptionistRequiredMixins, View):
    def get(self, request):
        today = timezone.localtime(timezone.now()).date()

        appointments = Appointment.objects.select_related(
            'patient', 'doctor__user'
        ).filter(
            appointment_date=today,
            status__in=['confirmed', 'checked_in']
        ).order_by('start_time')

        queue = AppointmentQueue.objects.select_related(
            'appointment__patient',
            'appointment__doctor__user',
        ).filter(
            appointment__appointment_date=today
        ).order_by('check_in_time')

        return render(request, 'receptionists/checkin_queue.html', {
            'appointments': appointments,
            'queue':        queue,
        })

    def post(self, request):
        appointment_id = request.POST.get('appointment_id')
        action         = request.POST.get('action')
        today          = timezone.localtime(timezone.now()).date()

        try:
            with transaction.atomic():
                appointment = get_object_or_404(Appointment, id=appointment_id)

                if appointment.appointment_date != today:
                    messages.error(request, "This appointment is not for today.")
                    return redirect('checkin_queue')

                if action == 'checkin':
                    if appointment.status.lower() != 'confirmed':
                        messages.error(request, "Only confirmed appointments can be checked in.")
                        return redirect('checkin_queue')

                    if AppointmentQueue.objects.filter(appointment=appointment).exists():
                        messages.warning(request, "Patient is already checked in.")
                        return redirect('checkin_queue')

                    appointment.status        = 'checked_in'
                    appointment.check_in_time = timezone.localtime(timezone.now())
                    appointment.save()

                    AppointmentQueue.objects.create(
                        appointment   = appointment,
                        check_in_time = appointment.check_in_time,
                        status        = 'waiting',
                    )
                    messages.success(request, f'{appointment.patient.get_full_name()} checked in.')

                elif action == 'no_show':
                    if appointment.status.lower() not in ['confirmed', 'requested']:
                        messages.error(request, "Cannot mark this appointment as no-show.")
                        return redirect('checkin_queue')

                    appointment.status = 'no_show'
                    appointment.save()
                    messages.success(request, f'{appointment.patient.get_full_name()} marked as no-show.')

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')

        return redirect('checkin_queue')
class RescheduleView(ReceptionistRequiredMixins, View):
    def post(self, request, appointment_id):
        appointment = get_object_or_404(
            Appointment.objects.select_related("doctor"),
            id=appointment_id,
        )

        appointment_date = request.POST.get("appointment_date")
        start_time = request.POST.get("start_time")
        reason = request.POST.get("reason", "")
        
        if not reason:
            messages.error(request, "Please provide a reason for rescheduling.")
            return redirect("bookings")

        if not appointment_date or not start_time:
            messages.error(request, "Please choose a date and available slot.")
            return redirect("bookings")

        try:
            new_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            new_time = datetime.strptime(start_time, "%H:%M").time()
        except ValueError:
            messages.error(request, "Invalid date or time.")
            return redirect("bookings")

        available_slots = get_available_slots(appointment.doctor, new_date)

        if not any(slot["start"] == new_time.strftime("%H:%M") for slot in available_slots):
            messages.error(request, "This slot is no longer available.")
            return redirect("bookings")

        old_date = appointment.appointment_date
        old_time = appointment.start_time

        end_time = (
            datetime.combine(new_date, new_time)
            + timedelta(minutes=appointment.doctor.session_duration)
        ).time()

        try:
            with transaction.atomic():
                appointment.appointment_date = new_date
                appointment.start_time = new_time
                appointment.end_time = end_time
                appointment.status = "CONFIRMED"
                appointment.save()

                AppointmentReschedule.objects.create(
                    appointment=appointment,
                    old_date=old_date,
                    old_time=old_time,
                    new_date=new_date,
                    new_time=new_time,
                    changed_by=request.user,
                    reason=reason or "Receptionist rescheduled the appointment.",
                )
                create_notification(
                    user=appointment.patient,
                    title="Appointment Rescheduled",
                    message=(f"Your appointment on with Dr {appointment.doctor.user.get_full_name()} on {old_date} at {old_time} has been rescheduled to {new_date} at {new_time}. "
                             f"Reason: {reason}"),
                    
                   notification_type=Notification.NotificationType.RESCHEDULED,
                )
            

            messages.success(request, "Appointment reschedule requested.")
            return redirect("bookings")


        except Exception:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect("bookings")
        


class SchedulesView(ReceptionistRequiredMixins, View):
    def get(self, request):
        doctors   = DoctorProfile.objects.select_related('user').all()
        schedules = DoctorSchedule.objects.select_related('doctor__user').all()
        paginator = Paginator(schedules, 10)
        page_obj  = paginator.get_page(request.GET.get('page', 1))

        return render(request, 'receptionists/schedules.html', {
            'doctors':   doctors,
            'schedules': page_obj,
            'page_obj':  page_obj,
            'form':      DoctorScheduleForm(),
            'exc_form':  DoctorScheduleExceptionForm(),
        })

    def post(self, request):
        action    = request.POST.get('action')
        doctors   = DoctorProfile.objects.select_related('user').all()
        schedules = DoctorSchedule.objects.select_related('doctor__user').all()
        form      = DoctorScheduleForm()
        exc_form  = DoctorScheduleExceptionForm()

        if action == 'add_schedule':
            form = DoctorScheduleForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Schedule added.')
                return redirect('schedules')

        elif action == 'add_exception':
            exc_form = DoctorScheduleExceptionForm(request.POST)
            if exc_form.is_valid():
                exc_form.save()
                messages.success(request, 'Exception added.')
                return redirect('schedules')

        paginator = Paginator(schedules, 10)
        page_obj  = paginator.get_page(request.GET.get('page', 1))

        return render(request, 'receptionists/schedules.html', {
            'doctors':   doctors,
            'schedules': page_obj,
            'page_obj':  page_obj,
            'form':      form,
            'exc_form':  exc_form,
        })


class EditScheduleView(ReceptionistRequiredMixins, View):
    def post(self, request, schedule_id):
        schedule = get_object_or_404(DoctorSchedule, id=schedule_id)
        form = DoctorScheduleForm(request.POST, instance=schedule)

        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated.')
        else:
            messages.error(request, 'Something went wrong. Please try again.')

        return redirect('schedules')

class DeleteScheduleView(ReceptionistRequiredMixins, View):
    def post(self, request, schedule_id):
        schedule = get_object_or_404(DoctorSchedule, id=schedule_id)
        schedule.delete()
        messages.error(request, 'Schedule deleted.')
        return redirect('schedules')
