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
    def clean(self):
        cleanded_data = super().clean()
        doctor = cleanded_data.get('doctor')
        day = cleanded_data.get('day_of_week')
        start = cleanded_data.get('start_time')
        end = cleanded_data.get('end_time')
        
        if start >=end:
            raise forms.ValidationError("End time must be after start time.")
        overlapping_schedules = DoctorSchedule.objects.filter(
            doctor=doctor,
            day_of_week=day,
            start_time__lt=end,
            end_time__gt=start,
        )
        if self.instance and self.instance.pk:
            overlapping_schedules = overlapping_schedules.exclude(pk=self.instance.pk)
        if overlapping_schedules.exists():
            raise forms.ValidationError("Schedule overlaps with another schedule.")
        return cleanded_data
        


class DoctorScheduleExceptionForm(forms.ModelForm):
    class Meta:
        model  = DoctorScheduleException
        fields = ['doctor', 'date', 'is_day_off', 'start_time', 'end_time']
        
        
        
        
        