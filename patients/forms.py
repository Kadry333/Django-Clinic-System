from django import forms
from django.core.validators import RegexValidator
from django.utils import timezone

from accounts.models import User
from appointments.models import Appointment, RescheduleRequest
from doctors.models import DoctorProfile


name_validator = RegexValidator(
    regex=r"^[a-zA-Z\s]+$",
    message="Use letters and spaces only.",
)

egyptian_mobile_validator = RegexValidator(
    regex=r"^01[0125][0-9]{8}$",
    message="Enter a valid Egyptian mobile number.",
)


class PatientProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        min_length=2,
        max_length=50,
        validators=[name_validator],
    )
    last_name = forms.CharField(
        min_length=2,
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


class PatientAppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["doctor", "appointment_date", "start_time"]
        widgets = {
            "appointment_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["doctor"].queryset = DoctorProfile.objects.select_related("user").all()

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data["appointment_date"]

        if appointment_date < timezone.localdate():
            raise forms.ValidationError("You cannot book an appointment in the past.")

        return appointment_date


class PatientRescheduleRequestForm(forms.ModelForm):
    class Meta:
        model = RescheduleRequest
        fields = ["preferred_date", "preferred_time", "reason"]
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "preferred_time": forms.TimeInput(attrs={"type": "time"}),
            "reason": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data["preferred_date"]

        if preferred_date and preferred_date < timezone.localdate():
            raise forms.ValidationError("You cannot request a past date.")

        return preferred_date