from django.urls import path
from .views import *
urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('dashboard/', dashboard),
    path('book_appointment/', book_appointment),
    path('cancel_appointment/', cancel_appointment),
    path('get_notifications/', get_notifications),
    path('mark_as_read/', mark_as_read),
    path('past_appointments/', past_appointment),
    path('get_presc/', generate_presc),
    path('logout/', logout)
]