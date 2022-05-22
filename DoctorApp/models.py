from django.db import models
from UserApp.models import User
# Create your models here.

class Doctor(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    special_code = models.ForeignKey('Specialities', on_delete=models.DO_NOTHING)
    qualification = models.TextField()
    dob = models.DateField()
    address = models.TextField()
    gender = models.CharField(max_length=1)
    fees = models.IntegerField()
    phone = models.CharField(max_length=10, unique=True)
    exp = models.TextField()


class Specialities(models.Model):
    code = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def get_speciality_dict():
        list = Specialities.objects.values_list()
        dict = {}
        for i in range(len(list)):
            dict[list[i][0]] = list[i][1]
        return dict

