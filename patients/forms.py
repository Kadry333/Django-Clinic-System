from django import forms
from accounts.forms import egyptian_mobile_validator, name_validator
from accounts.models import User


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
