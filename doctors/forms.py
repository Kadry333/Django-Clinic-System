from django import forms
from django.contrib.auth.models import Group

from accounts.models import User
from doctors.models import DoctorProfile


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
