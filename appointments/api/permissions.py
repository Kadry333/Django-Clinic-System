from rest_framework.permissions import BasePermission


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="patient").exists()
        )


class IsDoctor(BasePermission):
    def has_permission(self, request):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="doctor").exists()
        )
