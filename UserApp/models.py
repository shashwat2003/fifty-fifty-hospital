from statistics import mode
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):

    RECEPTIONIST = 1
    DOCTOR = 2
    PATIENT = 3

    ROLES_CHOICES = ((RECEPTIONIST, 'Receptionist'), (DOCTOR, 'Doctor'), (PATIENT, 'Patient'))
    role = models.PositiveSmallIntegerField(choices=ROLES_CHOICES)
    username = models.CharField(max_length=12, unique=True, null=True)


class Appointment(models.Model):

    doc_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doc_id')
    date_time = models.DateTimeField()
    aadhar = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aadhar')
    isApprovedByDoctor = models.BooleanField(default=False)
    isApprovedByReceptionist = models.BooleanField(default=False)