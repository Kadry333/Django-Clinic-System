from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username