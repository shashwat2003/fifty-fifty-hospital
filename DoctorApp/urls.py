from django.urls import path
from .views import *
urlpatterns = [
    path('speciality_code/', speciality_codes),
    path('special_docs/', speciality_based_docs),
    path('pending_apps/', pending_approval),
    path('change_status/', approve_or_reject_appointment),
    path('reshedule_app/', reshedule_appointment),
    path('register/', register),
    path('dashboard/', dashboard),
    path('login/', login),
    path('logout/', logout)
]