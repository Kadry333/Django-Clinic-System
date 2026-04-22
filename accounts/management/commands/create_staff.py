from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates initial staff accounts for testing'

    def handle(self, *args, **kwargs):

        doctor, created = User.objects.get_or_create(email='doctor@clinicms.com')
        doctor.set_password('password123#')
        doctor.first_name = 'Ahmed'
        doctor.last_name  = 'Ali'
        doctor.save()
        doctor.groups.add(Group.objects.get(name='doctor'))
        self.stdout.write(self.style.SUCCESS('Doctor created'))

        receptionist, created = User.objects.get_or_create(email='receptionist@clinicms.com')
        receptionist.set_password('password123#')
        receptionist.first_name = 'Sara'
        receptionist.last_name  = 'Mohamed'
        receptionist.save()
        receptionist.groups.add(Group.objects.get(name='receptionist'))
        self.stdout.write(self.style.SUCCESS('Receptionist created'))

        admin, created = User.objects.get_or_create(email='admin@clinicms.com')
        admin.set_password('password123#')
        admin.first_name = 'Omar'
        admin.last_name  = 'Hassan'
        admin.is_staff   = True
        admin.save()
        admin.groups.add(Group.objects.get(name='admin'))
        self.stdout.write(self.style.SUCCESS('Admin created'))