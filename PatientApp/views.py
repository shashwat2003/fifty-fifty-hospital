# Create your views here.
import json, re
from datetime import datetime
from django.http import HttpRequest, JsonResponse, HttpResponse

from DoctorApp.models import Doctor
from .models import Patient, Prescription
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from UserApp.models import User, Appointment, Payment, Notification

from django.template.loader import get_template

fields = {"fname":"First Name","lname":"Last Name","passw":"Password","cpassw":"Confirm Password",
"dob":"Date Of Birth","gender":"Gender","address":"Address","aadhar":"Aadhar","phone":"Mobile Number",
"email":"E-Mail Address","doc_id":"Doctor ID", "datetime":"Date and Time"}

def response(obj, code=200):
    return JsonResponse(obj, safe=False, status=code)
    

def login(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Patient Login Accepts ONLY POST Requests!"}, 405)
    try:
        POST_DATA = json.loads(request.body)
        aadhar = POST_DATA['aadhar']
        passw  = POST_DATA['passw']
        user = authenticate(request,username=aadhar, password=passw)
       

        if user is not None and user.role == User.PATIENT:
            auth_login(request, user)
            return response({"success":"Successful Login!"})
        else:
            return response({"error":"Invalid Aadhar or Password!"}, 400)
        

    except KeyError as Error:
        return response({"error": Error.args[0] + " not provided!"}, 501)
    
    except Exception as Error:
        print(Error)
        return response({"error": Error.args}, 500)
    

def register(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Patient Register requests only POST requests!"}, 405)

    try:
        POST_DATA = json.loads(request.body)
        fname = POST_DATA['fname'].strip()
        lname = POST_DATA['lname'].strip()
        phone = POST_DATA['phone'].strip()
        email = POST_DATA['email'].strip()
        aadhar = POST_DATA['aadhar'].strip()
        address = POST_DATA['address'].strip()
        gender = POST_DATA['gender'].strip()
        dob = datetime.strptime(POST_DATA['dob'], '%a %b %d %Y').strftime("%Y-%m-%d")
        history = POST_DATA['history'].strip()
        passw = POST_DATA['passw'].strip()
        cpassw = POST_DATA['cpassw'].strip()
        
        if User.objects.filter(username=aadhar).exists():
            return response({"error":"Patient Already Exists!"}, 400)

        if not re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", dob):
            return response({"error":"Invalid DOB!"}, 400)

        if fname == "":
            return response({"error":"First Name Cannot be Empty!"}, 400)
        if len(phone) != 10:
            return response({"error":"Invalid Mobile Number!"}, 400)
        if address == "":
            return response({"error":"Address Cannot be Empty!"}, 400)
        if gender not in ['Male', 'Female', 'Others']:
            return response({"error":"Invalid Gender!"}, 400)
            
        # if not re.search('[0-9]{12}', aadhar):
        #     return response({"error": "Invalid Aadhar Number!"}, 400)
        if aadhar == "":
            return response({"error": "Invalid Username!"}, 400)

                
        if(passw != cpassw or passw == "" or cpassw == ""):
            return response({"error":"Passwords Don't Match!"}, 400)

        if(re.search("[^a-zA-Z ]", fname)):
            return response({"error":"First Name can only contain letters!"}, 400)

        if(re.search("[^a-zA-Z ]", lname)):
            return response({"error":"Last Name can only contain letters!"}, 400)

        if(re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", passw) == None):
            return response({"error":"Password must contain one special character, one capital letter, one small letter and one digit!"}, 400)

        if(re.search("[a-z0-9]+@[a-z]+\.[a-z]{2,3}", email) == None):
            return response({"error":"Invalid E-Mail Address!"}, 400)
        
        user = User.objects.create_user(username=aadhar, password=passw, first_name = fname, last_name=lname, email=email,
                role=User.PATIENT)
        Patient.objects.create(user=user, phone=phone, address=address,gender=gender, dob=dob, history=history)
        return response({"success":"Account Creation Successful!"}, 201)
        
    except KeyError as Error:
        return response({"error": fields[Error.args[0]] + " not provided!"}, 501)

    except Exception as Error:
        print(Error)
        return response({"error": "Internal Server Error! Please Try again later!"}, 500)

def dashboard(request: HttpRequest):
    if request.user.is_authenticated and request.user.role == User.PATIENT:
        patient = Patient.objects.get(user=request.user)
        appointments = Appointment.objects.filter(aadhar=request.user, status__in=["pending","approved"])
        arr = []
        for i in appointments:
            obj = {}
            doc = Doctor.objects.get(user=i.doc_id)
            obj["doc_name"] = doc.user.first_name
            obj["doc_spec"] = doc.special_code.name
            obj["appointment"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
            obj["status"] = i.status.upper()
            obj["app_id"] = i.id
            arr.append(obj)
            
        count  = Notification.objects.filter(aadhar=request.user, isSeen=False).count()

        return response({"patient_details": {"fname":request.user.first_name,"lname":request.user.last_name,
        "email":request.user.email,"aadhar":request.user.username,"gender":patient.gender,"phone":patient.phone,
        "address":patient.address,"dob":patient.dob,"history":patient.history,"registered_date": patient.registered_date},
        "appointment_details": arr,"notis": count })

    else:
        return response({"error":"Unauthorised Access!"}, 401)

def get_notifications(request: HttpRequest):
    if request.user.is_authenticated and request.user.role == User.PATIENT:
        try:
            notis = Notification.objects.filter(aadhar= request.user, isSeen=False)
            arr = []
            for i in notis:
                obj = {}
                obj["noti_id"] = i.id
                obj["message"] = i.message
                obj["noti_time"] = i.noti_time.strftime("%a %b %d %Y, %I:%M:%S %p")
                arr.append(obj)
            return response({"notis":arr})
        
        except KeyError as Error:
            return response({"error": fields[Error.args[0]] + " not provided!"}, 501)

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Server Error! Please Try again later!"}, 500)


    else:
        return response({"error":"Unathourised Access"}, 401)

def mark_as_read(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Presception requests only POST requests!"}, 405)

    if request.user.is_authenticated and request.user.role == User.PATIENT:
        try:
            POST_DATA = json.loads(request.body)
            noti_id = POST_DATA["noti_id"]
            noti = Notification.objects.get(id=noti_id)
            noti.isSeen = True
            noti.save()
            
            return response({"success":"Marked as Read!"})
        
        except KeyError as Error:
            return response({"error": fields[Error.args[0]] + " not provided!"}, 501)

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Server Error! Please Try again later!"}, 500)


    else:
        return response({"error":"Unathourised Access"}, 401)

def book_appointment(request: HttpRequest):
    if request.user.is_authenticated and request.user.role == User.PATIENT:
        try:
            POST_DATA = json.loads(request.body)
            date_time = POST_DATA["datetime"]
            doc_id = POST_DATA["doc_id"]

            date_time = datetime.strptime(date_time, "%d/%m/%Y, %I:%M:%S %p")
           
            doc = Doctor.objects.get(user=User.objects.get(id=doc_id))
            app = Appointment.objects.create(date_time=date_time, doc_id=User.objects.get(id=doc_id), 
                    aadhar=User.objects.get(id=request.user.id))
            Payment.objects.create(app_id = app, amount=doc.fees, status="paid")
            return response({"success":"Appointment Booked Successfully!"})
        
        except KeyError as Error:
            return response({"error": fields[Error.args[0]] + " not provided!"}, 501)

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Server Error! Please Try again later!"}, 500)


    else:
        return response({"error":"Unauthorised Access!"}, 401)


def cancel_appointment(request: HttpRequest):
    if request.user.is_authenticated:
        try:
            POST_DATA = json.loads(request.body)
            app_id = POST_DATA["app_id"]
            app = Appointment.objects.get(id=app_id)
            payment = Payment.objects.get(app_id = app)
            payment.status="refund"
            payment.save()
            app.status = "cancelled"
            app.save()
            return response({"success":"Appointment Cancelled Successfully!"})
        
        except KeyError as Error:
            return response({"error": fields[Error.args[0]] + " not provided!"}, 501)

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Server Error! Please Try again later!"}, 500)


    else:
        return response({"error":"Unauthorised Access!"}, 401)

def logout(request:HttpRequest):
    if request.user.is_authenticated:
        auth_logout(request)
        return response({"success":"Logout Sucessfull!"})
    else:
        return response({"error":"Unauthorised Access!"}, 401)

def generate_presc(request: HttpRequest):
    if request.method != "POST":
        return response({"error": "Presception requests only POST requests!"}, 405)

    try:
        POST_DATA = json.loads(request.body)
        app_id = POST_DATA["app_id"]
        appointment  = Appointment.objects.get(id=app_id)
        presc = Prescription.objects.get(appointment=appointment)
        doc = Doctor.objects.get(user=appointment.doc_id)
        patient = Patient.objects.get(user=appointment.aadhar)

        template_path = 'presc.html'
        context = {'patient_details': {"name": appointment.aadhar.first_name + " " + appointment.aadhar.last_name,"address":patient.address, "phone":patient.phone}, 
        "appointment_details":{"date_time":appointment.date_time.strftime("%d/%m/%Y %I:%M:%S %p"),"doc_name":appointment.doc_id.first_name,"speciality":doc.special_code.name,"doc_num":doc.phone,"id":appointment.id,
        "disease":appointment.disease.name},
        "prescription": json.loads(presc.presc)}
        
        template = get_template(template_path)
        html = template.render(context)
        return HttpResponse(html)

    except Exception as Error:
        print(Error)
        return response({"error": "Internal Server Error! Please Try again later!"}, 500)

def past_appointment(request: HttpRequest):
    if request.user.is_authenticated and request.user.role == User.PATIENT:
        try:
            appointments = Appointment.objects.filter(aadhar=request.user, status="checked").order_by('-date_time')
            arr = []
            for i in appointments:
                doc = Doctor.objects.get(user=i.doc_id)
                obj = {}
                obj["app_id"] = i.id
                obj["doc_name"] = i.doc_id.first_name + " " +i.doc_id.last_name
                obj["doc_spec"] = doc.special_code.name
                obj["status"] = i.status.upper()
                obj["datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
                arr.append(obj)
            appointments = Appointment.objects.filter(aadhar=request.user, status__in=["rejected","cancelled"]).order_by('-date_time')
            arr2 = []
            for i in appointments:
                doc = Doctor.objects.get(user=i.doc_id)
                obj = {}
                obj["app_id"] = i.id
                obj["doc_name"] = i.doc_id.first_name + " " +i.doc_id.last_name
                obj["doc_spec"] = doc.special_code.name
                obj["status"] = i.status.upper()
                obj["datetime"] = i.date_time.strftime("%a %b %d %Y, %I:%M:%S %p")
                arr2.append(obj)


            return response({"checked_appointments": arr,"other_appointments": arr2})

        except Exception as Error:
            print(Error)
            return response({"error": "Internal Error Occurred"}, 500)
    else:
        return response({"error":"Unauthorised Access!"}, 401)
