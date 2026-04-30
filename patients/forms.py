from django import forms
from django.core.validators import RegexValidator
from accounts.models import User
name_validator = RegexValidator(
    regex=r"^[a-zA-Z\s]+$",
    message="Use letters and spaces only.",
)

mobile_validator = RegexValidator(
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
        validators=[mobile_validator],
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]



