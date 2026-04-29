from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied

from doctors.models import DoctorProfile


def resolve_user_and_doctor(request, doctor_id=None):
    user = request.user

    if user.is_doctor:
        current_user = "Doctor"
    elif user.is_receptionist:
        current_user = "Receptionist"
    elif user.is_admin:
        current_user = "Admin"
    else:
        current_user = "Unknown"

    if not user.is_doctor and doctor_id:
        doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
    else:
        doctor = get_object_or_404(DoctorProfile, user=user)

    return current_user, doctor


def validate_doctor_access(user, doctor):
    if user.is_doctor:
        if not hasattr(user, "doctorprofile"):
            raise PermissionDenied("Doctor profile not found.")

        if doctor != user.doctorprofile:
            raise PermissionDenied("You don't have permission for this doctor.")
