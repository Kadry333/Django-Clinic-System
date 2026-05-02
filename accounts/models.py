from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
# Create your models here.
egyptian_mobile_validator = RegexValidator(
    regex=r"^01[0125][0-9]{8}$",
    message="Enter a valid Egyptian mobile number"
)
name_validator = RegexValidator(
    regex=r"^[a-zA-Z\s]+$",
    message="Use letters and spaces only.",
)
class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=50,blank=False,validators=[name_validator,MinLengthValidator(3)])
    last_name = models.CharField(max_length=50,blank=False,validators=[name_validator,MinLengthValidator(3)])
    email = models.EmailField(unique=True,blank=False)
    phone = models.CharField(max_length=11, unique=True,validators=[egyptian_mobile_validator],blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']
    def __str__(self):
        return f"{self.get_full_name()}"
    
    def save(self, *args, **kwargs):
      if self.email:
          self.email = self.email.lower().strip()
      super().save(*args, **kwargs)
    
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
