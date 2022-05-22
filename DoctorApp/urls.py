from django.urls import path
from .views import *
urlpatterns = [
    path('speciality_code', speciality_codes),
    path('register', register),
    path('login', login)
]