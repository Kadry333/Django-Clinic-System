from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator

from accounts.mixins import ReceptionistRequiredMixins
from appointments.models import Appointment, AppointmentReschedule
from doctors.models import DoctorProfile, DoctorSchedule, DoctorScheduleException
from .forms import RescheduleForm, DoctorScheduleForm, DoctorScheduleExceptionForm



class ReceptionistDashboardView(ReceptionistRequiredMixins, View):
    def get(self, request):
        today = timezone.now().date()
        context = {
            'total_today':     Appointment.objects.filter(appointment_date=today).count(),
            'confirmed_today': Appointment.objects.filter(appointment_date=today, status='CONFIRMED').count(),
            'checked_in':      Appointment.objects.filter(appointment_date=today, status='CHECKED_IN').count(),
            'requested':       Appointment.objects.filter(appointment_date=today, status='REQUESTED').count(),
        }
        return render(request, 'receptionists/dashboard.html', context)


class BookingsView(ReceptionistRequiredMixins, View):
    def get(self, request):
        status = request.GET.get('status', '')
        date   = request.GET.get('date', '')

        appointments = Appointment.objects.select_related('patient', 'doctor').all()

        if status:
            appointments = appointments.filter(status=status)
        if date:
            appointments = appointments.filter(appointment_date=date)

        appointments = appointments.order_by('-appointment_date')

        paginator = Paginator(appointments, 10)
        page_obj  = paginator.get_page(request.GET.get('page', 1))

        context = {
            'appointments':   page_obj,
            'page_obj':       page_obj,
            'status_choices': Appointment.STATUS_CHOICES,
        }
        return render(request, 'receptionists/bookings.html', context)

    def post(self, request):
        appointment_id = request.POST.get('appointment_id')
        action         = request.POST.get('action')
        appointment    = get_object_or_404(Appointment, id=appointment_id)

        if action == 'confirm':
            if appointment.status == 'REQUESTED':
                appointment.status = 'CONFIRMED'
                appointment.save()
                messages.success(request, 'Appointment confirmed.')
            else:
                messages.error(request, 'Only requested appointments can be confirmed.')

        elif action == 'cancel':
            if appointment.status in ['REQUESTED', 'CONFIRMED']:
                appointment.status = 'CANCELLED'
                appointment.save()
                messages.success(request, 'Appointment cancelled.')
            else:
                messages.error(request, 'This appointment cannot be cancelled.')

        else:
            messages.error(request, 'Invalid action.')

        return redirect('bookings')


class CheckInQueueView(ReceptionistRequiredMixins, View):
    def get(self, request):
        today = timezone.now().date()
        queue = Appointment.objects.filter(
            appointment_date=today,
            status__in=['CONFIRMED', 'CHECKED_IN']
        ).select_related('patient', 'doctor').order_by('start_time')

        return render(request, 'receptionists/checkin_queue.html', {'queue': queue})

    def post(self, request):
        appointment_id = request.POST.get('appointment_id')
        appointment    = get_object_or_404(Appointment, id=appointment_id)
        today          = timezone.now().date()

        if appointment.appointment_date != today or appointment.status != 'CONFIRMED':
            messages.error(request, "Only today's confirmed appointments can be checked in.")
            return redirect('checkin_queue')

        appointment.status        = 'CHECKED_IN'
        appointment.check_in_time = timezone.now()
        appointment.save()
        messages.success(request, f'{appointment.patient.get_full_name()} checked in.')
        return redirect('checkin_queue')


class RescheduleView(ReceptionistRequiredMixins, View):
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

        return render(request, 'receptionists/reschedule.html', {
            'form':        form,
            'appointment': appointment,
        })


class SchedulesView(ReceptionistRequiredMixins, View):
    def get(self, request):
        doctors  = DoctorProfile.objects.select_related('user').all()
        schedules = DoctorSchedule.objects.select_related('doctor__user').all()

        paginator = Paginator(schedules, 10)
        page_obj  = paginator.get_page(request.GET.get('page', 1))

        context = {
            'doctors':   doctors,
            'schedules': page_obj,
            'page_obj':  page_obj,
            'form':      DoctorScheduleForm(),
            'exc_form':  DoctorScheduleExceptionForm(),
        }
        return render(request, 'receptionists/schedules.html', context)

    def post(self, request):
        action    = request.POST.get('action')
        doctors   = DoctorProfile.objects.select_related('user').all()
        schedules = DoctorSchedule.objects.select_related('doctor__user').all()

        # Start with empty forms
        form     = DoctorScheduleForm()
        exc_form = DoctorScheduleExceptionForm()

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

        # Re-render with errors if form was invalid
        paginator = Paginator(schedules, 10)
        page_obj  = paginator.get_page(request.GET.get('page', 1))

        return render(request, 'receptionists/schedules.html', {
            'doctors':   doctors,
            'schedules': page_obj,
            'page_obj':  page_obj,
            'form':      form,
            'exc_form':  exc_form,
        })


class DeleteScheduleView(ReceptionistRequiredMixins, View):
    def post(self, request, schedule_id):
        schedule = get_object_or_404(DoctorSchedule, id=schedule_id)
        schedule.delete()
        messages.success(request, 'Schedule deleted.')
        return redirect('schedules')

