from django import forms

from accounts.models import User
from accounts.forms import RegisterForm, egyptian_mobile_validator, name_validator


class PatientProfileForm(forms.ModelForm):
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
    email = forms.EmailField()
    phone = forms.CharField(
        max_length=11,
        validators=[egyptian_mobile_validator],
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower()
        return email


class AdminPatientCreateForm(RegisterForm):
    pass