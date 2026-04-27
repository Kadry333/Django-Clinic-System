from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def patient_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_patient:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def doctor_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_doctor:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def receptionist_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_receptionist:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_clinic_admin:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper