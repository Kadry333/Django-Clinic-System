from datetime import datetime

from django import forms
from django.core.validators import RegexValidator
from django.utils.dateparse import parse_date
from django.utils import timezone

from accounts.models import User
from appointments.models import RescheduleRequest
from doctors.models import DoctorProfile
from patients.services import get_available_slots


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


class PatientAppointmentBookingForm(forms.Form):
    doctor = forms.ModelChoiceField(
        queryset=DoctorProfile.objects.none(),
        empty_label="Select a doctor",
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    slot = forms.ChoiceField(
        choices=[],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop("doctor", None)
        appointment_date = kwargs.pop("appointment_date", None)
        require_slot = kwargs.pop("require_slot", False)
        super().__init__(*args, **kwargs)

        self.fields["doctor"].queryset = DoctorProfile.objects.select_related("user").all()
        self.require_slot = require_slot
        self.selected_doctor = doctor
        self.selected_appointment_date = appointment_date
        self.available_slots = []
        self._set_slot_choices([])

        if self.is_bound:
            doctor_id = self.data.get(self.add_prefix("doctor"))
            if doctor_id and self.selected_doctor is None:
                try:
                    self.selected_doctor = self.fields["doctor"].queryset.get(pk=doctor_id)
                except (DoctorProfile.DoesNotExist, ValueError, TypeError):
                    self.selected_doctor = None

            raw_appointment_date = self.data.get(self.add_prefix("appointment_date"))
            if raw_appointment_date and self.selected_appointment_date is None:
                self.selected_appointment_date = parse_date(raw_appointment_date)

        if self.selected_doctor and self.selected_appointment_date:
            self.available_slots = get_available_slots(
                self.selected_doctor,
                self.selected_appointment_date,
            )
            self._set_slot_choices(self.available_slots)

    def _set_slot_choices(self, slots):
        self.fields["slot"].choices = [
            ("", "Select an available slot"),
            *[(slot.strftime("%H:%M"), slot.strftime("%I:%M %p").lstrip("0")) for slot in slots],
        ]

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data["appointment_date"]

        if appointment_date < timezone.localdate():
            raise forms.ValidationError("You cannot book an appointment in the past.")

        return appointment_date

    def clean_slot(self):
        slot = self.cleaned_data.get("slot")

        if not slot:
            return None

        try:
            return datetime.strptime(slot, "%H:%M").time()
        except ValueError as exc:
            raise forms.ValidationError("Select a valid available slot.") from exc

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor") or self.selected_doctor
        appointment_date = cleaned_data.get("appointment_date") or self.selected_appointment_date
        slot = cleaned_data.get("slot")

        if doctor and appointment_date:
            self.selected_doctor = doctor
            self.selected_appointment_date = appointment_date
            self.available_slots = get_available_slots(doctor, appointment_date)
            self._set_slot_choices(self.available_slots)

        if self.require_slot and doctor and appointment_date:
            if not self.available_slots:
                raise forms.ValidationError("No available slots for this doctor on the selected date.")

            if not slot:
                self.add_error("slot", "Select an available slot.")
            elif slot not in self.available_slots:
                self.add_error("slot", "This slot is no longer available. Please choose another one.")

        return cleaned_data


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
