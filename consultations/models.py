from django.db import models
from appointments.models import Appointment


class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    drug_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    
    
class MedicalTest(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=255, default='Unknown')