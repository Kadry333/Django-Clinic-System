from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator

from accounts.mixins import ReceptionistRequiredMixins
from appointments.models import Appointment, AppointmentReschedule, AppointmentQueue
from doctors.models import DoctorProfile, DoctorSchedule, DoctorScheduleException
from .forms import RescheduleForm, DoctorScheduleForm, DoctorScheduleExceptionForm


class ReceptionistDashboardView(ReceptionistRequiredMixins, View):
    def get(self, request):
        today = timezone.now().date()
        context = {
            'total_today':     Appointment.objects.filter(appointment_date=today).count(),
            'confirmed_today': Appointment.objects.filter(appointment_date=today, status='confirmed').count(),
            'checked_in':      Appointment.objects.filter(appointment_date=today, status='checked_in').count(),
            'requested':       Appointment.objects.filter(status='requested').count(),
        }
        return render(request, 'receptionists/dashboard.html', context)


class BookingsView(ReceptionistRequiredMixins, View):
    def get(self, request):
        status = request.GET.get('status', '')
        date   = request.GET.get('date', '')

        appointments = Appointment.objects.select_related('patient', 'doctor__user').all()

        if status:
            appointments = appointments.filter(status=status.lower())
        if date:
            appointments = appointments.filter(appointment_date=date)

        appointments = appointments.order_by('-appointment_date')
        paginator    = Paginator(appointments, 10)
        page_obj     = paginator.get_page(request.GET.get('page', 1))

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
        status         = appointment.status.lower()

        if action == 'confirm':
            if status == 'requested':
                appointment.status = 'confirmed'
                appointment.save()
                messages.success(request, 'Appointment confirmed.')
            else:
                messages.error(request, 'Only requested appointments can be confirmed.')

        elif action == 'cancel':
            if status in ['requested', 'confirmed']:
                appointment.status = 'cancelled'
                appointment.save()
                messages.success(request, 'Appointment cancelled.')
            else:
                messages.error(request, 'This appointment cannot be cancelled.')

        return redirect('bookings')


class CheckInQueueView(ReceptionistRequiredMixins, View):
    def get(self, request):
        today = timezone.localtime(timezone.now()).date()
        print(today)

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
        appointment    = get_object_or_404(Appointment, id=appointment_id)
        today          = timezone.localtime(timezone.now()).date()

        if appointment.appointment_date != today:
            messages.error(request, "This appointment is not for today.")
            return redirect('checkin_queue')

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
            messages.success(request, 'Appointment rescheduled.')
            return redirect('bookings')

        return render(request, 'receptionists/reschedule.html', {
            'form':        form,
            'appointment': appointment,
        })


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


class DeleteScheduleView(ReceptionistRequiredMixins, View):
    def post(self, request, schedule_id):
        schedule = get_object_or_404(DoctorSchedule, id=schedule_id)
        schedule.delete()
        messages.success(request, 'Schedule deleted.')
        return redirect('schedules')
