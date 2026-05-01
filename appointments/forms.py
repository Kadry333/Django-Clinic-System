from django import forms

from appointments.models import AppointmentReschedule


class AppointmentRescheduleForm(forms.ModelForm):
    class Meta:
        model = AppointmentReschedule
        fields = ["new_date", "new_time", "reason"]
