from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']
    def __str__(self):
        return f"{self.get_full_name()}"
    
    @property
    def is_patient(self):
        return self.groups.filter(name='patient').exists()
    
    @property
    def is_doctor(self):
        return self.groups.filter(name='doctor').exists()
    
    @property
    def is_receptionist(self):
        return self.groups.filter(name='receptionist').exists()
    
    @property
    def is_admin(self):
        return self.groups.filter(name='admin').exists()