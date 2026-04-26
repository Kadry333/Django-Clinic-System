from django import forms
from django.contrib.auth.models import Group
from django.utils import timezone

from accounts.models import User
from doctors.models import DoctorProfile, DoctorSchedule, DoctorScheduleException


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields["password"].required = True

    def clean_email(self):
        email = self.cleaned_data["email"]
        existingUser = User.objects.filter(email=email)

        if self.instance and self.instance.pk:
            existingUser = existingUser.exclude(pk=self.instance.pk)

        if existingUser.exists():
            raise forms.ValidationError("A user with this email already exists.")

        return email


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ["specialization", "session_duration", "buffer_time"]


class DoctorScheduleExceptionForm(forms.ModelForm):
    class Meta:
        model = DoctorScheduleException
        fields = ["date", "start_time", "end_time", "is_day_off"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "is_day_off": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop("doctor", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        date = cleaned_data.get("date")
        is_day_off = cleaned_data.get("is_day_off")

        if is_day_off:
            return cleaned_data

        if date and date < timezone.localdate():
            raise forms.ValidationError("You cannot select a past date.")

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("End time must be after start time.")

        if self.doctor:
            weekday = date.weekday()

            schedule = DoctorSchedule.objects.filter(
                doctor=self.doctor, day_of_week=weekday
            ).first()

            if not schedule:
                raise forms.ValidationError("Doctor is not working on this day.")

            if start_time and end_time:
                if start_time < schedule.start_time or end_time > schedule.end_time:
                    raise forms.ValidationError(
                        f"Must be within working hours: "
                        f"{schedule.start_time} - {schedule.end_time}"
                    )

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("Start time must be before end time.")
