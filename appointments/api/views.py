from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from appointments.models import Appointment, AppointmentReschedule, RescheduleRequest
from .serializers import AppointmentSerializer
from appointments.services import get_available_slots
from doctors.models import DoctorProfile
from datetime import datetime, timedelta

from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination


class AppointmentPagination(PageNumberPagination):
    page_size = 10


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().select_related("doctor__user", "patient")
    serializer_class = AppointmentSerializer
    pagination_class = AppointmentPagination

    sort_map = {
        "doctor": ("doctor__user__first_name", "doctor__user__last_name"),
        "patient": ("patient__first_name", "patient__last_name"),
        "date": ("appointment_date", "start_time"),
        "start_time": ("start_time",),
        "session_duration": ("doctor__session_duration",),
        "status": ("status",),
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        search = params.get("search", "").strip()
        status_filter = params.get("status", "").strip()
        doctor_id = params.get("doctor", "").strip()
        patient_id = params.get("patient", "").strip()
        start_date = params.get("start_date", "").strip()
        end_date = params.get("end_date", "").strip()
        sort = params.get("sort", "date")
        direction = params.get("direction", "desc")

        if search:
            search_filter = (
                Q(patient__first_name__icontains=search)
                | Q(patient__last_name__icontains=search)
                | Q(patient__email__icontains=search)
            )
            if search.isdigit():
                search_filter |= Q(id=search)
            queryset = queryset.filter(search_filter)

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if start_date:
            queryset = queryset.filter(appointment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(appointment_date__lte=end_date)

        sort_fields = self.sort_map.get(sort, ("appointment_date", "start_time"))
        if direction == "desc":
            ordering = [f"-{field}" for field in sort_fields]
        else:
            ordering = list(sort_fields)

        return queryset.order_by(*ordering, "id")

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = "cancelled"
        appointment.save()
        return Response({"status": "cancelled"})

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = "confirmed"
        appointment.save()
        return Response({"status": "confirmed"})

    @action(detail=True, methods=["post"])
    def check_in(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = "checked_in"
        appointment.check_in_time = timezone.now()
        appointment.save()
        return Response({"status": "checked_in"})

    @action(detail=True, methods=["post"])
    def no_show(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = "no_show"
        appointment.save()
        return Response({"status": "no_show"})

    @action(detail=True, methods=["post"])
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        new_date_str = request.data.get("new_date")
        new_time_str = request.data.get("new_time")
        reason = request.data.get("reason", "")

        if not new_date_str or not new_time_str:
            return Response(
                {"error": "new_date and new_time are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
                new_time = None
                for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p"):
                    try:
                        new_time = datetime.strptime(new_time_str, fmt).time()
                        break
                    except ValueError:
                        continue

                if not new_time:
                    return Response(
                        {"error": "Invalid time format"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                old_date = appointment.appointment_date
                old_time = appointment.start_time

                end_time = (
                    datetime.combine(new_date, new_time)
                    + timedelta(minutes=appointment.doctor.session_duration)
                ).time()

                appointment.appointment_date = new_date
                appointment.start_time = new_time
                appointment.end_time = end_time
                appointment.save()

                AppointmentReschedule.objects.create(
                    appointment=appointment,
                    old_date=old_date,
                    old_time=old_time,
                    new_date=new_date,
                    new_time=new_time,
                    changed_by=request.user,
                    reason=reason,
                )

                RescheduleRequest.objects.filter(
                    appointment=appointment, status="pending"
                ).delete()

                return Response({"status": "rescheduled"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def approve_reschedule(self, request, pk=None):
        appointment = self.get_object()
        reschedule_request = (
            RescheduleRequest.objects.filter(appointment=appointment, status="pending")
            .order_by("-created_at")
            .first()
        )

        if not reschedule_request:
            return Response(
                {"error": "No pending reschedule request found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                old_date = appointment.appointment_date
                old_time = appointment.start_time
                new_date = reschedule_request.preferred_date
                new_time = reschedule_request.preferred_time

                end_time = (
                    datetime.combine(new_date, new_time)
                    + timedelta(minutes=appointment.doctor.session_duration)
                ).time()

                appointment.appointment_date = new_date
                appointment.start_time = new_time
                appointment.end_time = end_time
                appointment.status = "confirmed"
                appointment.save()

                AppointmentReschedule.objects.create(
                    appointment=appointment,
                    old_date=old_date,
                    old_time=old_time,
                    new_date=new_date,
                    new_time=new_time,
                    changed_by=request.user,
                    reason=reschedule_request.reason
                    or "Approved patient reschedule request.",
                )

                reschedule_request.status = "approved"
                reschedule_request.save()

                return Response({"status": "approved"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject_reschedule(self, request, pk=None):
        appointment = self.get_object()
        reschedule_request = (
            RescheduleRequest.objects.filter(appointment=appointment, status="pending")
            .order_by("-created_at")
            .first()
        )

        if not reschedule_request:
            return Response(
                {"error": "No pending reschedule request found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reschedule_request.status = "rejected"
        reschedule_request.save()

        return Response({"status": "rejected"})


@api_view(["GET"])
def available_slots(request):
    doctor_id = request.query_params.get("doctor_id")
    date_str = request.query_params.get("date")

    if not doctor_id or not date_str:
        return Response(
            {"error": "Missing doctor_id or date"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        doctor = DoctorProfile.objects.get(id=doctor_id)
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        slots = get_available_slots(doctor, date)
        return Response(slots)
    except:
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
