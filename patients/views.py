from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView, UpdateView

from accounts.mixins import AdminRequiredMixins, patientRequiredMixins
from consultations.models import Consultation
from notifications.models import Notification
from notifications.services import create_notification
from patients.forms import PatientProfileForm


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

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Patient"
        context["patient"] = self.request.user
        return context

    def form_valid(self, form):
        form.save()

        create_notification(
            user=self.request.user,
            title="Profile updated",
            notification_type=Notification.NotificationType.PROFILE_UPDATED,
            message="Your profile has been updated successfully.",
        )

        messages.success(self.request, "Your profile has been updated successfully.")
        return redirect("patients:profile")


class PatientConsultationSummaryView(patientRequiredMixins, ListView):
    model = Consultation
    template_name = "patients/consultation_summary.html"
    context_object_name = "consultations"

    def get_queryset(self):
        return (
            Consultation.objects.filter(
                appointment__patient=self.request.user,
                appointment__status="completed",
            )
            .select_related(
                "appointment",
                "appointment__doctor",
                "appointment__doctor__user",
            )
            .prefetch_related("prescription_set", "medicaltest_set")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Patient"
        return context


class AdminPatientsView(AdminRequiredMixins, TemplateView):
    template_name = "patients/admin_patients.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        User = get_user_model()

        search_query = self.request.GET.get("search", "").strip()

        patients = (
            User.objects.filter(groups__name="patient")
            .distinct()
            .order_by("first_name", "last_name", "email")
        )

        if search_query:
            patients = patients.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(phone__icontains=search_query)
            )

        paginator = Paginator(patients, 10)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        context["current_role"] = "Admin"
        context["patients"] = page_obj
        context["page_obj"] = page_obj
        context["search_query"] = search_query
        context["patients_count"] = patients.count()

        return context


class AdminPatientDetailView(AdminRequiredMixins, TemplateView):
    template_name = "patients/admin_patient_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()

        patient = get_object_or_404(
            User.objects.filter(groups__name="patient").distinct(),
            pk=self.kwargs["pk"],
        )

        context["current_role"] = "Admin"
        context["patient"] = patient
        return context


class AdminPatientProfileUpdateView(AdminRequiredMixins, UpdateView):
    form_class = PatientProfileForm
    template_name = "patients/profile_edit.html"

    def get_queryset(self):
        User = get_user_model()
        return User.objects.filter(groups__name="patient").distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_role"] = "Admin"
        context["patient"] = self.object
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Patient profile has been updated successfully.")
        return redirect("patients:admin")


class AdminPatientDeleteView(AdminRequiredMixins, View):
    def post(self, request, pk):
        User = get_user_model()

        patient = get_object_or_404(
            User.objects.filter(groups__name="patient").distinct(),
            pk=pk,
        )

        patient_name = patient.get_full_name() or patient.email
        patient.delete()

        messages.success(
            request,
            f"Patient '{patient_name}' was deleted successfully.",
        )

        return redirect("patients:admin")
