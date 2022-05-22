from django.db import models
from UserApp.models import User
# Create your models here.

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    gender = models.CharField(max_length=1)
    dob = models.DateField()
    history = models.TextField()

