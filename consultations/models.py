from django.db import models
from appointments.models import Appointment


class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    diagnosis   = models.TextField()
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation for {self.appointment}"


class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    drug_name    = models.CharField(max_length=255)
    dosage       = models.CharField(max_length=100)
    duration     = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.drug_name} — {self.dosage}"


class MedicalTest(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='tests')
    test_name    = models.CharField(max_length=255)

    def __str__(self):
        return self.test_name