from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from accounts.forms import RegisterForm, LoginForm
from django.contrib import messages

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
    def get(self,request):
        logout(request)
        # messages.info(request,"You have been logged out")
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