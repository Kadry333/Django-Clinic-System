from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class patientRequiredMixins(LoginRequiredMixin):
    def dispatch(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_patient:
            raise PermissionDenied
        return super().dispatch(request,*args,**kwargs)

class DoctorRequiredMixins(LoginRequiredMixin):
    def dispatch(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_doctor:
            raise PermissionDenied
        return super().dispatch(request,*args,**kwargs)
    
class ReceptionistRequiredMixins(LoginRequiredMixin):
    def dispatch(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_receptionist:
            raise PermissionDenied
        return super().dispatch(request,*args,**kwargs)
    
class AdminRequiredMixins(LoginRequiredMixin):
    def dispatch(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            raise PermissionDenied
        return super().dispatch(request,*args,**kwargs)
    
class StaffRequiredMixins(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_patient:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)