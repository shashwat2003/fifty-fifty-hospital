from django.urls import path
from .views import *
urlpatterns = [
    path('login/', login),
    path('logout/', logout),
    path('dashboard/', dashboard),
    path('doctor_search/', doctor_search),
    path('doctor_details/', doctor_details),
    path('doctor_past_apts/', doctor_past_appointments),
    path('pending_appointments/', pending_appointments),
    path('all_patients/', all_patients),
    path('patient_details/', patient_details),
    path('change_status/', approve_or_reject_appointment),
    path('report_date_wise/', generate_report_date_wise),
    path('report_disease_wise/', generate_report_disease_wise),
    
]