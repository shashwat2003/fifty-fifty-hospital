from django.urls import path
from .views import *
urlpatterns = [
    path('speciality_code/', speciality_codes),
    path('special_docs/', speciality_based_docs),
    path('register/', register),
    path('login/', login)
]