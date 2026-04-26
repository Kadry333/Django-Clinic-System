from django.shortcuts import render
from django.views import View
from appointments.models import Appointment
from doctors.models import DoctorProfile
from accounts.models import User
from django.db.models import Count, Sum
from django.db.models.functions import ExtractHour
from accounts.mixins import AdminRequiredMixins

class AnalyticsDashboardView(AdminRequiredMixins, View):
    def get(self, request):

        total_appointments = Appointment.objects.count()
        
        no_shows = Appointment.objects.filter(status='no_show').count()
        no_show_rate = (no_shows / total_appointments * 100) if total_appointments > 0 else 0
       
        total_revenue = Appointment.objects.filter(status='completed').aggregate(Sum('fee'))['fee__sum'] or 0
        
        active_doctors = DoctorProfile.objects.count()
        
        reception_team = User.objects.filter(groups__name='receptionist').count()

        peak_hours = Appointment.objects.annotate(
            hour=ExtractHour('start_time')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:3]

        context = {
            'total_appointments': total_appointments,
            'no_show_rate': round(no_show_rate, 2),
            'total_revenue': total_revenue,
            'active_doctors': active_doctors,
            'reception_team': reception_team,
            'peak_hours': peak_hours,
        }
        return render(request, 'analytics/admin_dashboard.html', context)
