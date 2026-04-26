from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255)
    session_duration = models.IntegerField(default=30)
    buffer_time = models.IntegerField(default=5)

    def __str__(self):
        return self.user.username


class DoctorSchedule(models.Model):
    DAYS = [
        ("mon", "Monday"),
        ("tue", "Tuesday"),
        ("wed", "Wednesday"),
        ("thu", "Thursday"),
        ("fri", "Friday"),
        ("sat", "Saturday"),
        ("sun", "Sunday"),
    ]

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()


class DoctorScheduleException(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    date = models.DateField()

    is_day_off = models.BooleanField(default=False)

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
