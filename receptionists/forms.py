from django import forms
from appointments.models import Appointment
from doctors.models import DoctorSchedule, DoctorScheduleException
from accounts.models import User
from accounts.forms import name_validator, egyptian_mobile_validator

# class ConfirmAppointmentForm(forms.ModelForm):
#     class Meta:
#         model  = Appointment
#         fields = ['status']


# class RescheduleForm(forms.ModelForm):
#     reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

#     class Meta:
#         model  = Appointment
#         fields = ['appointment_date', 'start_time', 'end_time']


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
        
        
        



class ReceptionistUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields["password"].required = True

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email:
            email = email.lower()

        existing_user = User.objects.filter(email=email)

        if self.instance.pk:
            existing_user = existing_user.exclude(pk=self.instance.pk)

        if existing_user.exists():
            raise forms.ValidationError("A user with this email already exists.")

        return email


        
        