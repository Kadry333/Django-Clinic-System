from django import forms
from appointments.models import Appointment, AppointmentReschedule
from doctors.models import DoctorSchedule, DoctorScheduleException


class ConfirmAppointmentForm(forms.ModelForm):
    """Receptionist confirms or cancels a requested appointment"""
    class Meta:
        model  = Appointment
        fields = ['status']


class RescheduleForm(forms.ModelForm):
    """Receptionist reschedules an appointment on behalf of a patient"""
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model  = Appointment
        fields = ['appointment_date', 'start_time', 'end_time']


class DoctorScheduleForm(forms.ModelForm):
    """Receptionist manages a doctor's weekly schedule"""
    class Meta:
        model  = DoctorSchedule
        fields = ['doctor', 'day_of_week', 'start_time', 'end_time']


class DoctorScheduleExceptionForm(forms.ModelForm):
    """Receptionist adds a vacation or one-off working day"""
    class Meta:
        model  = DoctorScheduleException
        fields = ['doctor', 'date', 'is_day_off', 'start_time', 'end_time', 'reason']