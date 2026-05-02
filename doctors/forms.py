from calendar import day_abbr

from django import forms
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import datetime, timedelta

from accounts.models import User
from doctors.models import DoctorProfile, DoctorSchedule, DoctorScheduleException
from accounts.forms import egyptian_mobile_validator, name_validator


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    first_name = forms.CharField(
        min_length=3,
        max_length=50,
        validators=[name_validator],
    )

    last_name = forms.CharField(
        min_length=3,
        max_length=50,
        validators=[name_validator],
    )

    phone = forms.CharField(
        max_length=11,
        validators=[egyptian_mobile_validator],
    )

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


class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = ["day_of_week", "start_time", "end_time"]
        widgets = {
            "day_of_week": forms.Select(choices=DoctorSchedule.DAYS),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop("doctor", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        day = cleaned_data.get("day_of_week")
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if not start:
            raise forms.ValidationError("Start time is required.")
        if not end:
            raise forms.ValidationError("End time is required.")
        if not day and day != 0:
            raise forms.ValidationError("Day of week is required.")

        if start >= end:
            raise forms.ValidationError("Start time must be before end time.")

        session_duration = self.doctor.session_duration

        start_date = datetime.combine(datetime.today(), start)
        end_date = datetime.combine(datetime.today(), end)

        if start_date + timedelta(minutes=session_duration) > end_date:
            raise forms.ValidationError(
                "Schedule must be long enough for at least one session."
            )

        schedules = DoctorSchedule.objects.filter(doctor=self.doctor, day_of_week=day)
        if self.instance and self.instance.pk:
            schedules = schedules.exclude(pk=self.instance.pk)

        is_valid = True
        for schedule in schedules:
            existing_start = schedule.start_time
            existing_end = schedule.end_time

            if start < existing_end and end > existing_start:
                is_valid = False
                break

        if not is_valid:
            raise forms.ValidationError(
                f"Schedule overlaps with existing schedule(s) for this day"
            )

        return cleaned_data


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
        day_abbr = {
            0: "mon",
            1: "tue",
            2: "wed",
            3: "thu",
            4: "fri",
            5: "sat",
            6: "sun",
        }
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
            weekday = day_abbr[date.weekday()]

            schedules = DoctorSchedule.objects.filter(
                doctor=self.doctor, day_of_week=weekday
            )
            if self.instance and self.instance.pk:
                schedules = schedules.exclude(pk=self.instance.pk)

            if not schedules.exists():
                raise forms.ValidationError("Doctor is not working on this day.")

            if start_time and end_time:
                is_valid = False

                for schedule in schedules:
                    if (
                        start_time >= schedule.start_time
                        and end_time <= schedule.end_time
                    ):
                        is_valid = True
                        break

                if not is_valid:
                    valid_ranges = ", ".join(
                        f"{s.start_time} - {s.end_time}" for s in schedules
                    )

                    raise forms.ValidationError(
                        f"Must be within working hours: {valid_ranges}"
                    )

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("Start time must be before end time.")
