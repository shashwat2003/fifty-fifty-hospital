import json
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from DoctorApp.models import Diseases, Doctor, Specialities
from django.db.models import Q
from UserApp.models import Appointment, Payment, User, Notification
from PatientApp.models import Patient
from datetime import datetime
# Create your views here.

def response(obj, code=200):
    return JsonResponse(obj, safe=False, status=code)

def login(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Receptionist Login Accepts only POST requests!"}, 405)
    else:
    
        POST_DATA = json.loads(request.body)
        username = POST_DATA["username"]
        passw = POST_DATA["passw"]
        user = authenticate(request, username=username, password=passw)
        if user is not None and user.role== User.RECEPTIONIST:
            auth_login(request, user)
            return response({"success":"Login Successful!"})
        else:
            return response({"error":"Invalid ID or password!"}, 400)



def dashboard(request: HttpRequest):
  
    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
        appointments = Appointment.objects.filter(status="approved").order_by('date_time')
        arr = []
        for i in appointments:
            obj = {}
            obj["app_id"] = i.id
            obj["patient_name"] = i.aadhar.first_name + " " + i.aadhar.last_name
            obj["doctor_name"] = i.doc_id.first_name + " " + i.doc_id.last_name
            obj["datetime"] =  i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr.append(obj)
        return response({"upcoming_appointments": arr})
    else:
        return response({"error":"Unauthorised Access"}, 401)


def pending_appointments(request: HttpRequest):
    
    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
        appointments  = Appointment.objects.filter(isApprovedByReceptionist=False, status="pending")
        arr = []
        for i in appointments:
            obj = {}
            obj["patient_name"] = i.aadhar.first_name + " " +i.aadhar.last_name
            obj["app_id"] = i.id
            obj["doc_name"] = i.doc_id.first_name + " " +i.doc_id.last_name
            obj["datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr.append(obj)
        return response({"pending_apts":arr})
    else:
        return response({"error":"Unauthorised Access"}, 401)
            

def doctor_search(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Accepts only POST requests!"})

    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
        POST_DATA = json.loads(request.body)
        special_code = int(POST_DATA["code"])
        hint = POST_DATA["hint"]
        arr = []
        if special_code == 0:
            users = User.objects.filter(Q(role=User.DOCTOR),Q(first_name__icontains=hint) | Q(last_name__icontains=hint))
            for i in users:
                obj = {}
                obj["doc_id"] = i.username
                obj["doc_name"] = i.first_name + " " + i.last_name
                obj["speciality"] = Doctor.objects.get(user=i).special_code.name
                obj["count_appointments"] = Appointment.objects.filter(doc_id=i, status="approved").count()
                obj["count_patients"] = Appointment.objects.filter(doc_id = i, status="checked").values('aadhar').distinct().count()
                arr.append(obj)
            return response({"result":arr})

        else:
            users = User.objects.filter(Q(role=User.DOCTOR),Q(first_name__icontains=hint) | Q(last_name__icontains=hint))
            special = Specialities.objects.get(code=special_code)
            docs = Doctor.objects.filter(special_code=special, user__in = users)
            for i in docs:
                obj = {}
                obj["doc_id"] = i.user.username
                obj["doc_name"] = i.user.first_name + " " + i.user.last_name
                obj["speciality"] = i.special_code.name
                obj["count_appointments"] = Appointment.objects.filter(doc_id=i.user, status="approved").count()
                obj["count_patients"] = Appointment.objects.filter(doc_id = i.user, status="checked").values('aadhar').distinct().count()
                arr.append(obj)
            return response({"result":arr})
    else:
        return response({"error":"Unauthorised Access"}, 401)
                
                

def doctor_details(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Accepts only POST requests!"})

    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
        POST_DATA = json.loads(request.body)
        doc_id = POST_DATA["doc_id"]
        user = User.objects.get(username=doc_id)
        doc = Doctor.objects.get(user=user)
        appointments = Appointment.objects.filter(doc_id = user, status="approved").order_by('date_time')
        arr = []
        for i in appointments:
            obj = {}
            obj["app_id"]=  i.id
            obj["patient_name"] = i.aadhar.first_name + " " + i.aadhar.last_name
            obj["app_datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr.append(obj)
        
        appointments = Appointment.objects.filter(doc_id = user, status="checked").values('aadhar').distinct()
        arr2 = []

        for i in appointments:
            user2 = User.objects.get(id=i["aadhar"])
            patient = Patient.objects.get(user = user2)
            latest = Appointment.objects.filter(doc_id = user, status="checked", aadhar=user2).order_by('-date_time')[0]
            obj = {}
            obj["patient_id"] = user2.id
            obj["patient_phone"] = patient.phone
            obj["patient_name"] = user2.first_name  + " " + user2.last_name
            obj["datetime"] = latest.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr2.append(obj)
        
        appointments = Appointment.objects.filter(doc_id=user, status="checked").order_by('-date_time')[:2]
        arr3 = []
        for i in appointments:
            obj = {}
            obj["patient_name"] = i.aadhar.first_name + " " +i.aadhar.last_name
            obj["datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr3.append(obj)
        
        return response({"doc_details": {"name":user.first_name + " " + user.last_name,"email":user.email
        ,"speciality": doc.special_code.name, "qualification": doc.qualification, 
        "dob": doc.dob.strftime("%a %b %d %Y"),"address":doc.address,"gender":doc.gender,
        "fees":doc.fees,"phone":doc.phone,"exp":doc.exp,"doc_id":doc_id},"upcoming_appointments":arr,"patients":arr2,"past_appointments":arr3})
    else:
        return response({"error":"Unauthorised Access"}, 401)
            
    

def doctor_past_appointments(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Accepts only POST requests!"})

    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
        POST_DATA = json.loads(request.body)
        doc_id = POST_DATA["doc_id"]
        user = User.objects.get(username=doc_id)
        appointments = Appointment.objects.filter(doc_id = user, status="checked").order_by('-date_time')
        arr = []
        for i in appointments:
            obj = {}
            obj["app_id"]=  i.id
            obj["patient_name"] = i.aadhar.first_name + " " + i.aadhar.last_name
            obj["aadhar"] = i.aadhar.username
            obj["app_datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr.append(obj)
        
        return response({"past_appointments": arr})
    else:
        return response({"error":"Unauthorised Access"}, 401)
                



def all_patients(request: HttpRequest):
  
    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
        # POST_DATA = json.loads(request.body)
        patients = Patient.objects.all()
        arr = []
        for i in patients:
            obj = {}
            obj["patient_id"] = i.user.id
            obj["aadhar"]=  i.user.username
            obj["patient_name"] = i.user.first_name + " " + i.user.last_name
            obj["dob"] = i.dob.strftime("%a %b %d %Y")
            obj["phone"] = i.phone
            obj["gender"] = i.gender
            obj["reg_date"] = i.registered_date.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr.append(obj)
        
        return response({"patients": arr})
    else:
        return response({"error":"Unauthorised Access"}, 401)
                

def patient_details(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Accepts only POST requests!"})
 
    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
        POST_DATA = json.loads(request.body)
        patient_id = POST_DATA["patient_id"]
        user = User.objects.get(id=patient_id)
        patient = Patient.objects.get(user=user)
        appointments = Appointment.objects.filter(aadhar = user, status="approved").order_by('date_time')
        arr = []
        for i in appointments:
            obj = {}
            obj["app_id"]=  i.id
            obj["doc_name"] = i.doc_id.first_name + " " + i.doc_id.last_name
            obj["app_datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr.append(obj)
        
        appointments = Appointment.objects.filter(aadhar = user, status="checked").values('doc_id').distinct()
        arr2 = []

        for i in appointments:
            user2 = User.objects.get(id=i["doc_id"])
            doctor = Doctor.objects.get(user = user2)
            latest = Appointment.objects.filter(aadhar = user, status="checked", doc_id=user2).order_by('-date_time')[0]
            obj = {}
            obj["doc_id"] = user2.username
            obj["doc_speciality"] = doctor.special_code.name
            obj["doc_name"] = user2.first_name + " " + user2.last_name
            obj["datetime"] = latest.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr2.append(obj)
        
        appointments = Appointment.objects.filter(aadhar=user, status="checked").order_by('-date_time')[:2]
        arr3 = []
        for i in appointments:
            obj = {}
            obj["doc_name"] = i.doc_id.first_name + " " +i.doc_id.last_name
            obj["datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr3.append(obj)
        
        return response({"patient_details": {"name":user.first_name + " " + user.last_name,"email":user.email, 
        "dob": patient.dob.strftime("%a %b %d %Y"),"address":patient.address,"gender":patient.gender,
        "history":patient.history,"phone":patient.phone,"reg_date":patient.registered_date},"upcoming_appointments":arr,"doctors":arr2,"past_appointments":arr3})
    else:
        return response({"error":"Unauthorised Access"}, 401)        


def approve_or_reject_appointment(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Approve/Reject accepts only POST requests!"}, 405)
    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
        POST_DATA = json.loads(request.body)
        app_id = POST_DATA["app_id"]
        status = POST_DATA["status"]
        print(POST_DATA)
        appointment = Appointment.objects.get(id=app_id)
        if(status):
            appointment.isApprovedByReceptionist = True
        else:
            appointment.isApprovedByReceptionist = False
            appointment.status = "rejected"
            payment = Payment.objects.get(app_id = appointment)
            payment.status="refund"
            payment.save()
            Notification.objects.create(aadhar=appointment.aadhar,
                message="Your appointment dated "+appointment.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")+" for "+
                appointment.doc_id.first_name+" has been rejected!")
        appointment.save()
        return response({"success": "Status changed!"})

    else:
        return response({"error":"Unauthorised Access"}, 401)

def logout(request:HttpRequest):
    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
        auth_logout(request)
        return response({"success":"Logout Sucessfull!"})
    else:
        return response({"error":"Unauthorised Access"}, 401)

def generate_report_date_wise(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Generate Report accepts only POST requests!"}, 405)
    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
    # if True:
        POST_DATA = json.loads(request.body)
        start_date = datetime.strptime(POST_DATA["start_date"],"%a %b %d %Y")
        end_date = datetime.strptime(POST_DATA["end_date"], "%a %b %d %Y")
        code = int(POST_DATA["code"])
        if code == 0:
            appointments = Appointment.objects.filter(date_time__gt=start_date, date_time__lt=end_date, status="checked")
            arr = []
            for i in appointments:
                obj = {}
                obj["app_id"] = i.id
                obj["doc_name"] = i.doc_id.first_name + " " + i.doc_id.last_name
                obj["patient_name"] = i.aadhar.first_name + " " + i.aadhar.last_name
                obj["datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
                arr.append(obj)

            return response({"appointments": arr})
        else:
            doctors = Doctor.objects.filter(special_code=Specialities.objects.get(code=code))
            users = []
            for i in doctors:
                users.append(i.user)
            # users = doctors.user_set.all()
            # users = User.objects.filter()
            appointments = Appointment.objects.filter(date_time__gt=start_date, date_time__lt=end_date, doc_id__in=users, status="checked")
            arr = []
            for i in appointments:
                obj = {}
                obj["app_id"] = i.id
                obj["doc_name"] = i.doc_id.first_name + " " + i.doc_id.last_name
                obj["patient_name"] = i.aadhar.first_name + " " + i.aadhar.last_name
                obj["datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
                arr.append(obj)

            return response({"appointments": arr})

    else:
        return response({"error":"Unauthorised Access"}, 401)

def generate_report_disease_wise(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Generate Report accepts only POST requests!"}, 405)
    if request.user.is_authenticated and request.user.role == User.RECEPTIONIST:
    # if True:
        POST_DATA = json.loads(request.body)
        start_date = datetime.strptime(POST_DATA["start_date"],"%a %b %d %Y")
        end_date = datetime.strptime(POST_DATA["end_date"], "%a %b %d %Y")
        d_id = POST_DATA["d_id"]
        disease = Diseases.objects.get(id=d_id)

        appointments = Appointment.objects.filter(date_time__gt=start_date, date_time__lt=end_date, status="checked", disease=disease)
        arr = []
        for i in appointments:
            obj = {}
            obj["app_id"] = i.id
            obj["doc_name"] = i.doc_id.first_name + " " + i.doc_id.last_name
            obj["patient_name"] = i.aadhar.first_name + " " + i.aadhar.last_name
            obj["datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr.append(obj)

        return response({"appointments": arr})
    else:
        return response({"error":"Unauthorised Access"}, 401)