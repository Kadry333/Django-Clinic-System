from django.db import models
from django.conf import settings
from doctors.models import DoctorProfile
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Appointment(models.Model):

    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)

    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    check_in_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('doctor', 'appointment_date', 'start_time'),
            ('patient', 'appointment_date', 'start_time'),
        ]



class AppointmentReschedule(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    old_date = models.DateField()
    old_time = models.TimeField()
    new_date = models.DateField()
    new_time = models.TimeField()
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    
    
class AppointmentQueue(models.Model):
    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.CASCADE
    )

    check_in_time = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("waiting", "Waiting"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        default="waiting"
    )

    def waiting_time(self):
        return int((timezone.now() - self.check_in_time).total_seconds() / 60)

    def __str__(self):
        return f"{self.appointment} - {self.status}"
    


class RescheduleRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    appointment = models.ForeignKey("appointments.Appointment", on_delete=models.CASCADE)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)

    reason = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)