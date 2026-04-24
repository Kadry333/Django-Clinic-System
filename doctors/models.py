from django.db import models
from accounts.models import User


class DoctorProfile(models.Model):
    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization   = models.CharField(max_length=255)
    session_duration = models.IntegerField(default=30)  # in minutes
    buffer_time      = models.IntegerField(default=5)   # in minutes

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class DoctorSchedule(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    doctor     = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time  = models.TimeField()
    end_time    = models.TimeField()

    def __str__(self):
        return f"{self.doctor} - {self.day_of_week}"


class DoctorScheduleException(models.Model):
    doctor     = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='exceptions')
    date       = models.DateField()
    is_day_off = models.BooleanField(default=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time   = models.TimeField(null=True, blank=True)
    reason     = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.doctor} - {self.date} ({'Off' if self.is_day_off else 'Working'})"