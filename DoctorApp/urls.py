from django.urls import path
from .views import *

urlpatterns = [
    path('speciality_code/', speciality_codes),
    path('special_docs/', speciality_based_docs),
    path('special_diseases/', speciality_based_diseases),
    path('pending_apps/', pending_approval),
    path('past_apps/', past_appointment),
    path('book_appointment/', book_appointment),
    path('add_presc/', add_prescript),
    path('change_status/', approve_or_reject_appointment),
    path('patient_details/', get_patient_details),
    path('reshedule_app/', reshedule_appointment),
    path('register/', register),
    path('dashboard/', dashboard),
    path('login/', login),
    path('logout/', logout),
]