from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import Group

from accounts.mixins import AdminRequiredMixins
from appointments.models import AppointmentQueue
from doctors.models import DoctorProfile, DoctorSchedule, DoctorScheduleException
from .forms import DoctorProfileForm, UserForm


def dashboard_view(request):
    doctor = DoctorProfile.objects.first()
    today = timezone.localtime(timezone.now()).date()

    queue = (
        AppointmentQueue.objects.select_related("appointment__patient")
        .filter(appointment__doctor=doctor, appointment__appointment_date=today)
        .order_by("check_in_time")
    )

    return render(
        request,
        "doctors/dashboard.html",
        {
            "current_role": "Doctor",
            "queue": queue,
        },
    )


def start_consultation(request, queue_id):
    q = get_object_or_404(AppointmentQueue, id=queue_id)

    q.status = "in_progress"
    q.save()

    return redirect("doctor_dashboard")


def finish_consultation(request, queue_id):
    return redirect("consultation_form", queue_id=queue_id)


def schedule_view(request):
    return render(
        request,
        "doctors/schedule.html",
        {
            "current_role": "Doctor",
        },
    )


class DoctorsListView(AdminRequiredMixins, View):
    sort_map = {
        "name": ("user__first_name", "user__last_name"),
        "email": ("user__email",),
        "specialization": ("specialization",),
        "session_duration": ("session_duration",),
        "buffer_time": ("buffer_time",),
    }

    def get(self, request):
        search_query = request.GET.get("search", "").strip()
        sort = request.GET.get("sort", "name")
        direction = request.GET.get("direction", "asc")

        doctors = DoctorProfile.objects.select_related("user")

        if search_query:
            search_filter = (
                Q(specialization__icontains=search_query)
                | Q(user__first_name__icontains=search_query)
                | Q(user__last_name__icontains=search_query)
                | Q(user__email__icontains=search_query)
            )

            if search_query.isdigit():
                search_filter |= Q(session_duration=int(search_query))
                search_filter |= Q(buffer_time=int(search_query))
            doctors = doctors.filter(search_filter)

        sort_fields = self.sort_map.get(sort, "name")
        if direction == "desc":
            ordering = [f"-{field}" for field in sort_fields]
        else:
            direction = "asc"
            ordering = list(sort_fields)

        doctors = doctors.order_by(*ordering)

        paginator = Paginator(doctors, 2)
        page_obj = paginator.get_page(request.GET.get("page", 1))

        return render(
            request,
            "doctors/list.html",
            {
                "doctors": page_obj,
                "page_obj": page_obj,
                "search_query": search_query,
                "current_sort": sort,
                "current_direction": direction,
                "current_role": "Doctor",
            },
        )


class DoctorDetailView(AdminRequiredMixins, View):
    def get(self, request, doctor_id):
        doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
        schedules = DoctorSchedule.objects.filter(doctor__id=doctor_id).order_by(
            "day_of_week", "start_time"
        )
        exceptions = DoctorScheduleException.objects.filter(
            doctor__id=doctor_id
        ).order_by("-date")

        return render(
            request,
            "doctors/detail.html",
            {
                "doctor": doctor,
                "schedules": schedules,
                "exceptions": exceptions,
                "current_role": "Doctor",
            },
        )


class DoctorCreateView(AdminRequiredMixins, View):
    def get(self, request):
        return render(
            request,
            "doctors/form.html",
            {
                "user_form": UserForm(),
                "doctor_form": DoctorProfileForm(),
                "page_title": "Create Doctor",
                "page_heading": "Create Doctor",
                "submit_label": "Create doctor",
                "current_role": "Doctor",
            },
        )

    def post(self, request):
        user_form = UserForm(request.POST)
        doctor_form = DoctorProfileForm(request.POST)

        if user_form.is_valid() and doctor_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            doctor_group, is_created = Group.objects.get_or_create(name="doctor")
            user.groups.add(doctor_group)

            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()

            messages.success(request, "Doctor created successfully.")
            return redirect("doctors.detail", doctor_id=doctor.id)

        return render(
            request,
            "doctors/form.html",
            {
                "user_form": user_form,
                "doctor_form": doctor_form,
                "page_title": "Create Doctor",
                "page_heading": "Create Doctor",
                "submit_label": "Create doctor",
                "current_role": "Doctor",
            },
        )


class DoctorEditView(AdminRequiredMixins, View):
    def get(self, request, doctor_id):
        doctor = get_object_or_404(DoctorProfile.objects, pk=doctor_id)

        return render(
            request,
            "doctors/form.html",
            {
                "user_form": UserForm(instance=doctor.user),
                "doctor_form": DoctorProfileForm(instance=doctor),
                "doctor": doctor,
                "page_title": "Edit Doctor",
                "page_heading": "Edit Doctor",
                "submit_label": "Save changes",
                "current_role": "Doctor",
            },
        )

    def post(self, request, doctor_id):
        doctor = get_object_or_404(DoctorProfile, pk=doctor_id)

        user_form = UserForm(request.POST, instance=doctor.user)
        doctor_form = DoctorProfileForm(request.POST, instance=doctor)

        if user_form.is_valid() and doctor_form.is_valid():

            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get("password")
            if password:
                user.set_password(password)
            user.save()

            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()

            messages.success(request, "Doctor updated successfully.")
            return redirect("doctors.detail", doctor_id=doctor.id)

        return render(
            request,
            "doctors/form.html",
            {
                "user_form": user_form,
                "doctor_form": doctor_form,
                "doctor": doctor,
                "page_title": "Edit Doctor",
                "page_heading": "Edit Doctor",
                "submit_label": "Save changes",
                "current_role": "Doctor",
            },
        )


class DoctorDeleteView(AdminRequiredMixins, View):
    def post(self, request, doctor_id):
        doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
        user = doctor.user
        user.delete()
        messages.success(request, "Doctor deleted successfully.")
        return redirect("doctors.list")
