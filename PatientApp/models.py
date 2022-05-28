from pyexpat import model
from django.db import models
from UserApp.models import Appointment, User
# Create your models here.

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    gender = models.CharField(max_length=6)
    dob = models.DateField()
    history = models.TextField()
    registered_date = models.DateField(auto_now_add=True)

class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    presc = models.TextField()

