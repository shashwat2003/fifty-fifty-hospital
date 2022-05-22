# Create your views here.
import json, re, bcrypt
from operator import truediv
from datetime import datetime
from django.http import HttpRequest, JsonResponse
from .models import Patient
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from UserApp.models import User

fields = {"fname":"First Name","lname":"Last Name","passw":"Password","cpassw":"Confirm Password",
"dob":"Date Of Birth","gender":"Gender","address":"Address","aadhar":"Aadhar","phone":"Mobile Number",
"email":"E-Mail Address"}

def response(obj, code=200):
    response = JsonResponse(obj, safe=False, status=code)
    # response["Access-Control-Allow-Credentials"] = True
    response["Access-Control-Allow-Origin"] = "http://127.0.0.1"
    response["Access-Control-Allow-Headers"] = "http://127.0.0.1"
    # response.set_cookie('SameSite','None')
    return response

def login(request: HttpRequest):
    if request.method != "POST":
        return response({"error":"Patient Login Accepts ONLY POST Requests!"}, 405)
    #POST_DATA = request.POST
    # else:
    #     user = authenticate(request,username='123456789123', password='Pass@123')
    
    #     if user is not None:
    #         auth_login(request, user)
    #         return response({"success":"Successful Login!"})
    #     else:
    #         return response({"error":"Invalid Aadhar or Password!"}, 400)
    try:
        POST_DATA = json.loads(request.body)
        aadhar = POST_DATA['aadhar']
        passw  = POST_DATA['passw']
        user = authenticate(request,username=aadhar, password=passw)
       

        if user is not None:
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
        aadhar = str(POST_DATA['aadhar'])
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
        if gender not in ['M', 'F', 'O']:
            return response({"error":"Invalid Gender!"}, 400)
            
        if not re.search('[0-9]{12}', aadhar):
            return response({"error": "Invalid Aadhar Number!"}, 400)
                
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
        
        user = User.objects.create_user(username=aadhar, password=passw, first_name = fname, last_name=lname, email=email)
        Patient.objects.create(user=user, phone=phone, address=address,gender=gender, dob=dob, history=history)
        # passw = bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt())
        # Patient.objects.create(fname=fname, lname=lname, phone=phone, email=email, aadhar=aadhar,
        # address=address, gender=gender, dob=dob, history=history, passw=passw )
        return response({"success":"Account Creation Successful!"}, 201)
        
    except KeyError as Error:
        return response({"error": fields[Error.args[0]] + " not provided!"}, 501)

    except Exception as Error:
        print(Error)
        return response({"error": "Internal Server Error! Please Try again later!"}, 500)

def dashboard(request: HttpRequest):
    if request.user.is_authenticated:
        patient = Patient.objects.get(user=request.user)
        print(patient)
        return response({"patient_details": {"fname":request.user.first_name,"lname":request.user.last_name,
        "email":request.user.email,"aadhar":request.user.username,"gender":patient.gender,"phone":patient.phone,
        "address":patient.address,"dob":patient.dob,"history":patient.history} })

    else:
        return response({"error":"Bhaisahab y kuch zyada nhi ho gaya?"})

def logout(request:HttpRequest):
    auth_logout(request)
    return response({"success":"Logout Sucessfull!"})
