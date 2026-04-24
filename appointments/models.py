from django.db import models
from accounts.models import User


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED',  'Requested'),
        ('CONFIRMED',  'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('COMPLETED',  'Completed'),
        ('CANCELLED',  'Cancelled'),
        ('NO_SHOW',    'No Show'),
    ]

    patient          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    appointment_date = models.DateField()
    start_time       = models.TimeField()
    end_time         = models.TimeField()
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    check_in_time    = models.DateTimeField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} with Dr.{self.doctor} on {self.appointment_date}"


class AppointmentReschedule(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reschedules')
    old_date    = models.DateField()
    old_time    = models.TimeField()
    new_date    = models.DateField()
    new_time    = models.TimeField()
    changed_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason      = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)