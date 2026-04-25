from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from accounts.mixins import patientRequiredMixins
from patients.forms import PatientProfileForm
from notifications.models import Notification


class PatientProfileView(patientRequiredMixins, TemplateView):
    template_name = "patients/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Patient"
        context["patient"] = self.request.user
        return context


class PatientProfileUpdateView(patientRequiredMixins, UpdateView):
    form_class = PatientProfileForm
    template_name = "patients/profile_edit.html"
    success_url = reverse_lazy("patients:my_profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Patient"
        context["patient"] = self.request.user
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        Notification.objects.create(
            user=self.request.user,
            title="Profile updated",
            message="Your profile has been updated successfully.",
        )

        messages.success(self.request, "Your profile has been updated successfully.")
        return response