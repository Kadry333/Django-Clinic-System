from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from accounts.forms import RegisterForm, LoginForm, UserUpdateForm
from django.contrib import messages
from django.contrib.messages import get_messages
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from receptionists.models import ReceptionistProfile


class RegisterView(View):
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = RegisterForm()
        return render(request,'accounts/register.html',{'form':form})
    
    def post(self,request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            patient_group, created = Group.objects.get_or_create(name='patient')
            user.groups.add(patient_group)
            login(request,user)
            return redirect('dashboard')
        return render(request,'accounts/register.html',{'form':form})
    
class LoginView(View):
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = LoginForm()
        return render(request,'accounts/login.html',{'form':form})
    def post(self,request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('dashboard')
        return render(request,'accounts/login.html',{'form':form})
    
class LogoutView(View):
    def post(self, request):
        # Clear leftover messages
        storage = get_messages(request)
        for _ in storage:
            pass

        logout(request)
        return redirect('login')

class DashboardView(LoginRequiredMixin,View):
    def get(self,request):
        user = request.user
        if user.is_patient:
            return redirect('book_appointment')
        elif user.is_doctor:
            return redirect('doctor_dashboard')
        elif user.is_receptionist:
            return redirect('receptionist_dashboard')
        else:
            return redirect('admin_dashboard')

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        form = UserUpdateForm(instance=user)
        profile_data = None
        if user.is_doctor:
            profile_data = DoctorProfile.objects.filter(user=user).first()
        elif user.is_patient:
            profile_data = PatientProfile.objects.filter(user=user).first()
        elif user.is_receptionist:
            profile_data = ReceptionistProfile.objects.filter(user=user).first()
            
        return render(request, 'accounts/profile.html', {
            'user': user,
            'profile_data': profile_data,
            'form': form
        })

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        
        return render(request, 'accounts/profile.html', {'form': form})
