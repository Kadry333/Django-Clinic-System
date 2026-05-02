from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from accounts.models import User
from doctors.models import DoctorProfile
from django.core.validators import RegexValidator

name_validator = RegexValidator(
    regex=r"^[a-zA-Z\s]+$",
    message="Use letters and spaces only.",
)

egyptian_mobile_validator = RegexValidator(
    regex=r"^01[0125][0-9]{8}$",
    message="Enter a valid Egyptian mobile number.",
)


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        min_length=3, max_length=50, validators=[name_validator]
    )
    last_name = forms.CharField(
        min_length=3, max_length=50, validators=[name_validator]
    )
    email = forms.EmailField()
    phone = forms.CharField(max_length=11, validators=[egyptian_mobile_validator])

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower()
        return email


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput())

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower()
        return email


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "w-full px-4 py-3 rounded-2xl border border-slate-200 focus:border-teal-500 focus:ring-4 focus:ring-teal-50 outline-none transition-all"
                }
            )


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ["specialization", "session_duration", "buffer_time", "session_fee"]
        labels = {
            "specialization": "Specialization",
            "session_duration": "Session Duration (Min)",
            "buffer_time": "Buffer Time (Min)",
            "session_fee": "Session Fee",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "w-full px-4 py-3 rounded-2xl border border-slate-200 focus:border-teal-500 focus:ring-4 focus:ring-teal-50 outline-none transition-all"
                }
            )
