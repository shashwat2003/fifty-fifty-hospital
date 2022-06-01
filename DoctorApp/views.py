from shutil import ExecError
from time import strftime
from django.http import HttpRequest, JsonResponse

from PatientApp.models import Patient, Prescription
from .models import Diseases, Specialities
from datetime import date, datetime
import re, bcrypt, json
from .models import Doctor
from UserApp.models import Appointment, User, Notification, Payment
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

# Create your views here.
fields = {"fname":"First Name","lname":"Last Name","passw":"Password","cpassw":"Confirm Password",
"dob":"Date Of Birth","gender":"Gender","address":"Address","exp":"Work Experience","phone":"Mobile Number",
"email":"E-Mail Address", "fees":"fees", "special_code":"Speciality Code", "qualification":"Qualification", "app_id":"App ID","doc_id":"Doctor ID"}

def response(obj, code=200):
    return JsonResponse(obj, status=code, safe=False)

def speciality_codes(request: HttpRequest):
    return response(Specialities.get_speciality_dict())

def speciality_based_docs(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Doctor Accepts ONLY POST Requests!"}, 405)

    if request.user.is_authenticated:
        try: 
            POST_DATA = json.loads(request.body)
            code = int(POST_DATA["code"])
            if code == 0:
                docs = Doctor.objects.all()
                obj = {}
                for i in docs:
                    obj[i.user.id] = {"name": i.user.first_name, "fees": i.fees}
                return response(obj)
            else:
                code = Specialities.objects.get(code=code)
                docs = Doctor.objects.filter(special_code = code)
                obj = {}
                for i in docs:
                    obj[i.user.id] = {"name": i.user.first_name, "fees": i.fees}
                return response(obj)

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Error Occurred"}, 500)
    else:
        return response({"error":"User Not authenticated!"}, 405)

def speciality_based_diseases(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Doctor Accepts ONLY POST Requests!"}, 405)

    if request.user.is_authenticated:
        try: 
            POST_DATA = json.loads(request.body)
            code = int(POST_DATA["code"])
            if code == 0:
                diseases = Diseases.objects.all()
                obj = {}
                for i in diseases:
                    obj[i.id] = i.name 
                return response(obj)
            else:
                code = Specialities.objects.get(code=code)
                docs = Diseases.objects.filter(special_code = code)
                obj = {}
                for i in docs:
                    obj[i.id] = i.name
                return response(obj)

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Error Occurred"}, 500)
    else:
        return response({"error":"User Not authenticated!"}, 405)
        


def login(request: HttpRequest):

    if request.method != "POST":
        return response({"error":"Patient Login Accepts ONLY POST Requests!"}, 405)
    #POST_DATA = request.POST

    try:
        POST_DATA = json.loads(request.body)
        doc_id = POST_DATA['doc_id'].strip()
        passw  = POST_DATA['passw']
        user = authenticate(username= doc_id, password=passw)
        if user is not None and user.role == User.DOCTOR:
            auth_login(request, user)
            return response({"success":"Successful Login!"})
        else:
            return response({"error":"Invalid DOC ID or Password!"}, 400)


    except KeyError as Error:
        return response({"error": fields[Error.args[0]] + " not provided!"}, 501)
    
    except Exception as Error:
        return response({"error": Error.args}, 500)

def register(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Doctor Register requests only POST requests!"}, 405)

    try:
        POST_DATA = json.loads(request.body)
        fname = POST_DATA['fname'].strip()
        lname = POST_DATA['lname'].strip()
        special_code = int(POST_DATA['special_code'])
        qualification = POST_DATA['qualification'].strip()
        dob = datetime.strptime(POST_DATA['dob'], '%a %b %d %Y').strftime("%Y-%m-%d")
        address = POST_DATA['address'].strip()
        gender = POST_DATA['gender'].strip()
        fees = POST_DATA['fees']
        email = POST_DATA['email'].strip()
        phone = POST_DATA['phone'].strip()
        exp = POST_DATA['exp'].strip()
        passw = POST_DATA['passw'].strip()
        cpassw = POST_DATA['cpassw'].strip()

        if Doctor.objects.filter(phone=phone).exists():
            return response({"error":"Mobile Number already exists!"}, 400)
        
        if special_code not in Specialities.get_speciality_dict():
            return response({"error":"Invalid Speciality Code!"}, 400)

        if not re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", dob):
            return response({"error":"Invalid DOB!"}, 400)
        if exp == "":
            return response({"error":"Experience Cannot be Empty!"}, 400)
        if qualification == "":
            return response({"error":"Qualification Cannot be Empty!"}, 400)
        if fname == "":
            return response({"error":"Name Cannot be Empty!"}, 400)
        if not re.search('[0-9]{10}', phone):
            return response({"error":"Invalid Mobile Number!"}, 400)
        if address == "":
            return response({"error":"Address Cannot be Empty!"}, 400)
        if gender not in ['Male', 'Female', 'Other']:
            return response({"error":"Invalid Gender!"}, 400)
            
        if fees < 0:
            return response({"error": "Enter a Valid Fees Value!"}, 400)
                
        if(passw != cpassw or passw == "" or cpassw == ""):
            return response({"error":"Passwords Don't Match!"}, 400)

        if(re.search("[^a-zA-Z .]", fname)):
            return response({"error":"Name can only contain letters!"}, 400)
        if(re.search("[^a-zA-Z .]", fname)):
            return response({"error":"Name can only contain letters!"}, 400)


        if(re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", passw) == None):
            return response({"error":"Password must contain one special character, one capital letter, one small letter and one digit and must be of 8 characters!"}, 400)

        if(re.search("[a-z0-9]+@[a-z]+\.[a-z]{2,3}", email) == None):
            return response({"error":"Invalid E-Mail Address!"}, 400)
        user = User.objects.create_user(username='doc_id',password=passw, first_name = fname, last_name=lname, email=email, role=User.DOCTOR)

        #Generating DOC ID
        username = 'D' + str(special_code) +str(user.id)
        user.username = username
        user.save()
        Doctor.objects.create(user=user,special_code=Specialities.objects.get(code=special_code), qualification=qualification,
        phone=phone, address=address,gender=gender, dob=dob, exp=exp,fees=fees)
        return response({"success":"Account Creation Successful! \n Your Doctor ID is "+ user.username + "\n The same has been sent to your mail: " + user.email}, 201)
    
        
    except KeyError as Error:
        return response({"error": fields[Error.args[0]] + " not provided!"}, 501)

    except Exception as Error:
        print(Error)
        return response({"error": "Internal Error Occurred"}, 500)

def dashboard(request: HttpRequest):
    print(request.user.is_authenticated)
    if request.user.is_authenticated and request.user.role == User.DOCTOR:
        # doctor = Doctor.objects.get(user=request.user)
        appointments = Appointment.objects.filter(doc_id = request.user, status="approved").order_by('date_time')
        arr = []
        for i in appointments:
          obj = {}
          obj["app_id"]=  i.id
          obj["patient_name"] = i.aadhar.first_name + " " + i.aadhar.last_name
          obj["app_datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
          arr.append(obj)

        appointments = Appointment.objects.filter(doc_id = request.user, status="checked").values('aadhar').distinct()
        arr2 = []

        for i in appointments:
            user = User.objects.get(id=i["aadhar"])
            patient = Patient.objects.get(user = user)
            latest = Appointment.objects.filter(doc_id = request.user, status="checked", aadhar=user).order_by('-date_time')[0]
            obj = {}
            obj["patient_id"] = user.id
            obj["patient_phone"] = patient.phone
            obj["patient_name"] = user.first_name
            obj["datetime"] = latest.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            arr2.append(obj)
        return response({"doc_name":request.user.first_name + request.user.last_name,"upcoming_appointments": arr,"patients": arr2 })
    else:
        return response({"error":"Unauthorised Access!"}, 401)

def approve_or_reject_appointment(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Approve/Reject accepts only POST requests!"}, 405)
    if request.user.is_authenticated and request.user.role == User.DOCTOR:
        try:
            POST_DATA = json.loads(request.body)
            app_id = POST_DATA["app_id"]
            status = POST_DATA["status"]
            print(POST_DATA)
            appointment = Appointment.objects.get(id=app_id)
            if(status):
                appointment.isApprovedByDoctor = True
                appointment.status = "approved"
                Notification.objects.create(aadhar=appointment.aadhar,
                    message="Your appointment dated "+appointment.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")+" for "+
                    appointment.doc_id.first_name+" has been approved!")
            else:
                appointment.isApprovedByDoctor = False
                appointment.status = "rejected"
                payment = Payment.objects.get(app_id = appointment)
                payment.status="refund"
                payment.save()
                Notification.objects.create(aadhar=appointment.aadhar,
                    message="Your appointment dated "+appointment.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")+" for "+
                    appointment.doc_id.first_name+" has been rejected!")
            appointment.save()
            return response({"success": "Status changed!"})

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Error Occurred"}, 500)
    else:
        return response({"error":"Unauthorised Access!"}, 401)

def reshedule_appointment(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Re-schedule appointments accepts only POST requests!"}, 405)
    if request.user.is_authenticated and request.user.role == User.DOCTOR:
        try:
            POST_DATA = json.loads(request.body)
            app_id = POST_DATA["app_id"]
            date_time = POST_DATA["datetime"]
            date_time = datetime.strptime(date_time, "%d/%m/%Y, %I:%M:%S %p")
            appointment = Appointment.objects.get(id=app_id)
            appointment.date_time = date_time
            appointment.save()
            Notification.objects.create(aadhar=appointment.aadhar,
            message="Your Appointment has been re-sheduled to "+date_time.strftime("%d/%m/%Y, %I:%M:%S %p")+"! Sorry for the inconveneince!")
            return response({"success": "ReSheduled!"})


        except Exception as Error:
            print(Error)
            return response({"error": "Internal Error Occurred"}, 500)
    else:
        return response({"error":"Unauthorised Access!"}, 401)

def book_appointment(request: HttpRequest):
    if request.user.is_authenticated and request.user.role == User.DOCTOR:
        try:
            POST_DATA = json.loads(request.body)
            date_time = POST_DATA["datetime"]
            patient_id = POST_DATA["patient_id"]
            date_time = datetime.strptime(date_time, "%d/%m/%Y, %I:%M:%S %p")
            app = Appointment.objects.create(date_time=date_time, aadhar=User.objects.get(id=patient_id), 
                    doc_id=User.objects.get(id=request.user.id), isApprovedByReceptionist=True, isApprovedByDoctor=True, status="approved")
            Payment.objects.create(app_id = app, amount=Doctor.objects.get(user=request.user).fees, status="paid")
            return response({"success":"Appointment Booked Successfully!"})
        
        except KeyError as Error:
            return response({"error": fields[Error.args[0]] + " not provided!"}, 501)

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Server Error! Please Try again later!"}, 500)

    else:
        return response({"error":"Unauthorised Access"}, 401)

def past_appointment(request: HttpRequest):
    if request.user.is_authenticated and request.user.role == User.DOCTOR:
        try:
            appointments = Appointment.objects.filter(doc_id=request.user, status="checked").order_by('-date_time')
            arr = []
            for i in appointments:
                obj = {}
                obj["app_id"] = i.id
                obj["patient_name"] = i.aadhar.first_name + " " +i.aadhar.last_name
                obj["datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
                arr.append(obj)

            return response({"past_appointments": arr})

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Error Occurred"}, 500)
    else:
        return response({"error":"Unauthorised Access"}, 401)


def pending_approval(request: HttpRequest):
    if request.user.is_authenticated and request.user.role == User.DOCTOR:
        try:
            appointments = Appointment.objects.filter(doc_id=request.user, status="pending", isApprovedByReceptionist=True)
            arr = []
            for i in appointments:
                obj = {}
                obj["patient_name"] = i.aadhar.first_name + " "+ i.aadhar.last_name
                obj["datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
                obj["app_id"] = i.id
                arr.append(obj)
            return response({"pending_approval": arr})

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Error Occurred"}, 500)
    else:
        return response({"error":"Unauthorised Access"}, 401)


def get_patient_details(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Patient Details accepts only POST requests!"}, 405)

    if request.user.is_authenticated and request.user.role == User.DOCTOR:
        try:
            POST_DATA = json.loads(request.body)
            patient_id = POST_DATA["patient_id"]
            user = User.objects.get(id=patient_id)
            patient = Patient.objects.get(user=user)

            appointments = Appointment.objects.filter(aadhar=user, doc_id=request.user, status="checked").order_by('-date_time')
            arr = []
            for i in appointments:
                obj = {}
                obj["app_id"] = i.id
                obj["date_time"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
                arr.append(obj)
            return response({"patient_details": {"fname":user.first_name,"lname":user.last_name,
            "email":user.email,"aadhar":user.username,"gender":patient.gender,"phone":patient.phone,
            "address":patient.address,"dob":patient.dob,"history":patient.history,"registered_date": patient.registered_date},
            "appointment_details": arr })

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Error Occurred"}, 500)
    else:
        return response({"error":"Unauthorised Access"}, 401)


def add_prescript(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Add Prescription accepts only POST requests!"}, 405)
    if request.user.is_authenticated and request.user.role == User.DOCTOR:
        try:
            POST_DATA = json.loads(request.body)
            app_id = POST_DATA["app_id"]
            disease_id = POST_DATA["d_id"]
            presc = json.dumps(POST_DATA["presc"])
            appointment = Appointment.objects.get(id=app_id)

            if Prescription.objects.filter(appointment=appointment).exists():
                return response({"error": "Prescription Allready Exists!"}, 403)

            appointment.status = "checked"
            appointment.disease = Diseases.objects.get(id=disease_id)
            appointment.save()
            Prescription.objects.create(appointment=appointment, presc =presc)
            Notification.objects.create(aadhar=appointment.aadhar, message="Your prescription dated "+
                appointment.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")+" by " + 
                appointment.doc_id.first_name +" has been added")
            return response({"success": "Prescription has been added and a notification has been sent to the patient!"})

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Error Occurred"}, 500)
    else:
        return response({"error":"Unauthorised Access"}, 401)


def logout(request:HttpRequest):
    if request.user.is_authenticated and request.user.role == User.DOCTOR:
        auth_logout(request)
        return response({"success":"Logout Sucessfull!"})
    else:
        return response({"error":"Unauthorised Access"}, 401)

