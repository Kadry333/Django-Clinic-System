from django import forms
from appointments.models import Appointment, AppointmentReschedule
from doctors.models import DoctorSchedule, DoctorScheduleException


class ConfirmAppointmentForm(forms.ModelForm):
    class Meta:
        model  = Appointment
        fields = ['status']


class RescheduleForm(forms.ModelForm):
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model  = Appointment
        fields = ['appointment_date', 'start_time', 'end_time']


class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model  = DoctorSchedule
        fields = ['doctor', 'day_of_week', 'start_time', 'end_time']


class DoctorScheduleExceptionForm(forms.ModelForm):
    class Meta:
        model  = DoctorScheduleException
        fields = ['doctor', 'date', 'is_day_off', 'start_time', 'end_time']