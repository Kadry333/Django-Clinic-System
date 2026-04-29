from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Creates the default groups for the clinic system'

    def handle(self, *args, **kwargs):

        patient_group,      _ = Group.objects.get_or_create(name='patient')
        doctor_group,       _ = Group.objects.get_or_create(name='doctor')
        receptionist_group, _ = Group.objects.get_or_create(name='receptionist')
        admin_group,        _ = Group.objects.get_or_create(name='admin')

        # Patient permissions
        patient_permissions = Permission.objects.filter(codename__in=[
            'view_appointment',      
            'add_appointment',      
            'delete_appointment',    
            'view_consultation',     
        ])
        patient_group.permissions.set(patient_permissions)

        doctor_permissions = Permission.objects.filter(codename__in=[
            'view_appointment',      
            'change_appointment',    
            'view_consultation',     
            'add_consultation',      
            'change_consultation',   
            'view_doctorschedule',  
            'view_appointmentqueue', 
        ])
        doctor_group.permissions.set(doctor_permissions)

        receptionist_permissions = Permission.objects.filter(codename__in=[
            'view_appointment',      
            'change_appointment',    
            'add_doctorschedule',   
            'change_doctorschedule', 
            'delete_doctorschedule', 
            'view_doctorschedule',   
            'view_appointmentqueue', 
            'change_appointmentqueue'
        ])
        receptionist_group.permissions.set(receptionist_permissions)

        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)

        self.stdout.write(self.style.SUCCESS('Groups and permissions created successfully!'))