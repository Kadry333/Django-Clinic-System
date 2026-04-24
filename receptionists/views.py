from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils import timezone

from accounts.mixins import ReceptionistRequiredMixins
from appointments.models import Appointment, AppointmentReschedule
from doctors.models import DoctorProfile, DoctorSchedule, DoctorScheduleException
from accounts.models import User
from .forms import RescheduleForm, DoctorScheduleForm, DoctorScheduleExceptionForm


class ReceptionistDashboardView(ReceptionistRequiredMixins, View):
    def get(self, request):
        today = timezone.now().date()

        # Summary numbers for the dashboard cards
        context = {
            'total_today':     Appointment.objects.filter(appointment_date=today).count(),
            'confirmed_today': Appointment.objects.filter(appointment_date=today, status='CONFIRMED').count(),
            'checked_in':      Appointment.objects.filter(appointment_date=today, status='CHECKED_IN').count(),
            'requested':       Appointment.objects.filter(status='REQUESTED').count(),
        }
        return render(request, 'receptionists/dashboard.html', context)


class BookingsView(ReceptionistRequiredMixins, View):
    """List of all appointments — receptionist can confirm or cancel"""
    def get(self, request):
        # Filters from query string
        status = request.GET.get('status', '')
        date   = request.GET.get('date', '')

        appointments = Appointment.objects.select_related('patient', 'doctor').all()

        if status:
            appointments = appointments.filter(status=status)
        if date:
            appointments = appointments.filter(appointment_date=date)

        context = {
            'appointments': appointments.order_by('-appointment_date'),
            'status_choices': Appointment.STATUS_CHOICES,
        }
        return render(request, 'receptionists/bookings.html', context)

    def post(self, request):
        """Confirm or cancel an appointment"""
        appointment_id = request.POST.get('appointment_id')
        action         = request.POST.get('action')  # 'confirm' or 'cancel'
        appointment    = get_object_or_404(Appointment, id=appointment_id)

        if action == 'confirm':
            appointment.status = 'CONFIRMED'
            messages.success(request, 'Appointment confirmed.')
        elif action == 'cancel':
            appointment.status = 'CANCELLED'
            messages.success(request, 'Appointment cancelled.')

        appointment.save()
        return redirect('bookings')


class CheckInQueueView(ReceptionistRequiredMixins, View):
    """Shows today's appointments — receptionist checks patients in"""
    def get(self, request):
        today = timezone.now().date()

        # Today's confirmed appointments ordered by start time
        queue = Appointment.objects.filter(
            appointment_date=today,
            status__in=['CONFIRMED', 'CHECKED_IN']
        ).select_related('patient', 'doctor').order_by('start_time')

        context = {'queue': queue}
        return render(request, 'receptionists/checkin_queue.html', context)

    def post(self, request):
        """Mark a patient as checked in"""
        appointment_id = request.POST.get('appointment_id')
        appointment    = get_object_or_404(Appointment, id=appointment_id)

        appointment.status        = 'CHECKED_IN'
        appointment.check_in_time = timezone.now()
        appointment.save()

        messages.success(request, f'{appointment.patient.get_full_name()} checked in.')
        return redirect('checkin_queue')


class RescheduleView(ReceptionistRequiredMixins, View):
    """Receptionist reschedules an appointment and saves the history"""
    def get(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        form        = RescheduleForm(instance=appointment)
        return render(request, 'receptionists/reschedule.html', {
            'form':        form,
            'appointment': appointment,
        })

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        form        = RescheduleForm(request.POST, instance=appointment)

        if form.is_valid():
            # Save the old values in the audit trail before changing
            AppointmentReschedule.objects.create(
                appointment = appointment,
                old_date    = appointment.appointment_date,
                old_time    = appointment.start_time,
                new_date    = form.cleaned_data['appointment_date'],
                new_time    = form.cleaned_data['start_time'],
                changed_by  = request.user,
                reason      = form.cleaned_data['reason'],
            )
            form.save()
            messages.success(request, 'Appointment rescheduled successfully.')
            return redirect('bookings')

        return render(request, 'receptionists/schedules.html', {
            'form':        form,
            'appointment': appointment,
        })


class SchedulesView(ReceptionistRequiredMixins, View):
    """Receptionist views and manages all doctor schedules"""
    def get(self, request):
        doctors   = DoctorProfile.objects.select_related('user').all()
        schedules = DoctorSchedule.objects.select_related('doctor__user').all()
        form      = DoctorScheduleForm()
        exc_form  = DoctorScheduleExceptionForm()

        context = {
            'doctors':   doctors,
            'schedules': schedules,
            'form':      form,
            'exc_form':  exc_form,
        }
        return render(request, 'receptionists/reschedule.html', context)

    def post(self, request):
        """Add a new schedule or exception"""
        action = request.POST.get('action')  # 'add_schedule' or 'add_exception'

        if action == 'add_schedule':
            form = DoctorScheduleForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Schedule added.')
            else:
                messages.error(request, 'Please fix the errors.')

        elif action == 'add_exception':
            exc_form = DoctorScheduleExceptionForm(request.POST)
            if exc_form.is_valid():
                exc_form.save()
                messages.success(request, 'Exception added.')
            else:
                messages.error(request, 'Please fix the errors.')

        return redirect('schedules')


class DeleteScheduleView(ReceptionistRequiredMixins, View):
    """Delete a doctor schedule"""
    def post(self, request, schedule_id):
        schedule = get_object_or_404(DoctorSchedule, id=schedule_id)
        schedule.delete()
        messages.success(request, 'Schedule deleted.')
        return redirect('schedules')