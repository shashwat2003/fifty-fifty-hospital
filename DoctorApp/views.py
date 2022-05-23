from django.http import HttpRequest, JsonResponse
from .models import Specialities
from datetime import datetime
import re, bcrypt, json
from .models import Doctor
from UserApp.models import User
from django.contrib.auth import authenticate, login as auth_login

# Create your views here.
fields = {"fname":"First Name","lname":"Last Name","passw":"Password","cpassw":"Confirm Password",
"dob":"Date Of Birth","gender":"Gender","address":"Address","exp":"Work Experience","phone":"Mobile Number",
"email":"E-Mail Address", "fees":"fees", "special_code":"Speciality Code", "qualification":"Qualification"}

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
            code = POST_DATA["code"]
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
        


def login(request: HttpRequest):

    if request.method != "POST":
        return response({"error":"Patient Login Accepts ONLY POST Requests!"}, 405)
    #POST_DATA = request.POST

    try:
        POST_DATA = json.loads(request.body)
        doc_id = POST_DATA['doc_id'].strip()
        passw  = POST_DATA['passw']
        user = authenticate(username= doc_id, password=passw)
        if user is not None:
            auth_login(request, user)
            return response({"success":"Successful Login!"})
        else:
            return response({"error":"Invalid DOC ID or Password!"}, 400)
    
        

    except KeyError as Error:
        return response({"error": Error.args[0] + " not provided!"}, 501)
    
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
        if gender not in ['M', 'F', 'O']:
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
    pass

