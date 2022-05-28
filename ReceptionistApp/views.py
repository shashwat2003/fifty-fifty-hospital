import json
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from DoctorApp.models import Doctor, Specialities
from django.db.models import Q
from UserApp.models import Appointment, User

# Create your views here.

def response(obj, code=200):
    return JsonResponse(obj, safe=False, status=code)

def login(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Receptionist Login Accepts only POST requests!"}, 405)
    else:
        try:
            POST_DATA = json.loads(request.body)
            username = POST_DATA["username"]
            passw = POST_DATA["passw"]
            user = authenticate(request, username=username, password=passw)
            if user is not None and user.role== User.RECEPTIONIST:
                auth_login(request, user)
                return({"success":"Login Successful!"})
            else:
                return({"error":"Invalid ID or password!"}, 400)

        except Exception as Error:
            print(Error)
            return response({"error":"Internal Server Error!"}, 500)

def dashboard(request: HttpRequest):
    try:
        if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
            appointments = Appointment.objects.filter(status="approved")
            arr = []
            for i in appointments:
                obj = {}
                obj[""]
    except Exception as Error:
        return response({"error":"Internal Server Error!"}, 500)

def doctor_search(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Accepts only POST requests!"})
    try:
        if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
            POST_DATA = json.loads(request.body)
            special_code = int(POST_DATA["code"])
            hint = POST_DATA["hint"]
            arr = []
            if special_code == -1:
                users = User.objects.filter(Q(role=User.DOCTOR),Q(first_name__icontains=hint) | Q(last_name__icontains=hint))
                for i in users:
                    obj = {}
                    obj["doc_id"] = i.username
                    obj["doc_name"] = i.first_name + " " + i.last_name
                    obj["count_appointments"] = Appointment.objects.filter(doc_id=i, status="approved").count()
                    obj["count_patients"] = Appointment.objects.filter(doc_id = i, status="checked").values('aadhar').distinct().count()
                    arr.append(obj)
                return response({"result":arr})

            else:
                users = User.objects.filter(Q(role=User.DOCTOR),Q(first_name__icontains=hint) | Q(last_name__icontains=hint))
                special = Specialities.objects.get(id=special_code)
                docs = Doctor.objects.filter(special=special, user__in = users)
                for i in docs:
                    obj = {}
                    obj["doc_id"] = i.user.username
                    obj["doc_name"] = i.user.first_name + " " + i.user.last_name
                    obj["count_appointments"] = Appointment.objects.filter(doc_id=i.user, status="approved").count()
                    obj["count_patients"] = Appointment.objects.filter(doc_id = i.user, status="checked").values('aadhar').distinct().count()
                    arr.append(obj)
                return response({"result":arr})
                
                
    except Exception as Error:
        print(Error)
        return response({"error":"Internal Server Error!"}, 500)