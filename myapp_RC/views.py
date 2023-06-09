from django.shortcuts import render
from django.http import JsonResponse
from myapp_RC.models import *
from django.contrib.auth.models import User # Using a django in built library to store or register the user in our database
from django.contrib import messages  # To display messagess after the the user has registered successfully
from django.shortcuts import redirect, render
from django.contrib.auth import login,authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
import re
import random
import datetime
import requests
import time
import json
from django.http import JsonResponse

def home(request):
    return render(request, "myapp_RC/signin.html")

def signup(request):
    if request.method == "POST":
        nusername = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        nemail = request.POST['email']
        pass2 = request.POST['pass2']
        pass1 = request.POST['pass1']
        mobno = request.POST['mobno']
        category = request.POST['categories']
        
        # Verify user Credentials
        if User.objects.filter(username = nusername).exists() :
            messages.error(request,"Username already  Exists")
        elif  User.objects.filter(email = nemail).exists():
            messages.error(request,"Email is already register")
        elif pass1 != pass2 :
            messages.error(request,"Confirmed Password did not match the entered Password")
        elif (len(pass1) < 8):
            messages.error(request,"Password should contain atleast 8 characters")
        elif not re.search("[a-z]", pass1):
            messages.error(request,"Password should contain atleast one Lowercase letter")
        elif not re.search("[A-Z]", pass1):
            messages.error(request,"Password should contain atleast one Uppercase letter")
        elif not re.search("[0-9]", pass1):
            messages.error(request,"Password should contain atleast one Number")
        elif not re.search("[_@!#%$]", pass1):
            messages.error(request,"Password should contain atleast one Special character")
        elif mobno.isnumeric() == False or len(mobno) != 10 :
            messages.error(request,"Enter a valid Mobile number")
        else :    
            myuser=User.objects.create_user(username=nusername, password=pass1, email=nemail)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.save()
            if category == '1':
                newuserprofile=Profile(user = myuser, mob_no = mobno, category = True)

            elif category == '0':
                newuserprofile=Profile(user = myuser, mob_no = mobno, category = False)
            newuserprofile.save()
            # messages.success(request, "Your account has been successfully created!")

            # Redirect the user to the signin page once the successful registration
            return redirect('/signin')
        return redirect('/signup')
    return render(request, "myapp_RC/signup.html")

def signin(request):
    context ={}
    try :
        if request.method == 'POST':
            username = request.POST['username']
            pass1 = request.POST['pass1']
            # team_value = request.POST.get('flexRadioDefault') # 1 for team, 2 for individual
            user = authenticate(username = username, password = pass1)

            if user is not None:
                login(request, user)
                # fname = user.first_name                
                profile = Profile.objects.get(user = user)
                
                # Alloting question list
                if profile.category == True:   # True for Junior
                    allQues = Question.objects.filter(is_junior = True)
                else:
                    allQues = Question.objects.filter(is_junior = False)
                queIndex = [q.id for q in allQues]
                random.shuffle(queIndex)
                queIndex = queIndex[:30]
                profile.questionIndexList = str(queIndex)

                # Prevent Re-login
                if profile.newlogin == False :
                    profile.newlogin = True
                else :
                    messages.error(request, "Already Logged in via other device")
                    return render(request, 'myapp_RC/signin.html', context)
                profile.save()
                return redirect('Instruction')
            else:
                messages.error(request, "Bad Credentials")
                return render(request, "myapp_RC/signin.html")
    except :
        return redirect ('SignIn')

    return render( request, "myapp_RC/signin.html")

def signout(request):
    try :
        # Store logouttime in case of accidental logout
        ruser = request.user
        profile = Profile.objects.get(user = ruser)
        profile.remainingTime = profile.remainingTime -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None)).seconds 
        profile.logoutTime = datetime.datetime.now()
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('/home')
    except :
        return redirect('/home')

@login_required(login_url = 'SignIn')
def instruction(request):
    try :
        if request.method == 'POST':
            # Start timer as soon as code reaches here
            ruser = request.user
            profile = Profile.objects.get(user = ruser)
            profile.startTime = datetime.datetime.now()
            profile.save()
            request.method = "GET"
            return QuestionView(request)
    except :
        return redirect('Instruction')
    return render(request,"myapp_RC/instruction.html")

@never_cache
@login_required(login_url = 'SignIn')
def QuestionView(request):
    context = { }
    ruser = request.user
    profile = Profile.objects.get(user = ruser)
    context['currquestNum'] = profile.quesno # Current question no. to display
    qList = eval(profile.questionIndexList) # Question list
    currQues = Question.objects.get(id=qList[0])    
    context["currquest"] = currQues.question

    # Marking Scheme
    context['plusmrks'] = 4
    context['minusmrks'] = 0

    # Passing profile
    context["profile"] = profile

    context["users"] = list(Profile.objects.filter(category = bool(profile.category)).order_by('marks',"accuracy","remainingTime").reverse())
    
    # Create easy question no. as soon as fuel is 3
    if profile.lifeline1_count == 3 and profile.lifeline1_using == False:
        profile.lifeline1_status = True
        currQueslist = EasyQuestion.objects.all()
        profile.lifeline1_question_id = (random.randrange(len(currQueslist)))
        profile.save()

    # Handling reload
    if request.method == 'GET':
        if profile.isFirstTry == 0:
            context["res1"] = profile.cache
        context["currquest"] = currQues.question
        context['plusmrks'] = profile.plusmrks
        context['minusmrks'] = profile.minusmrks
        context["profile"] = profile
        context["second1"] = (datetime.timedelta(seconds = profile.remainingTime) -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None))).seconds
        return render(request, 'myapp_RC/question.html',context)
    if True:
        try:
            if profile.isFirstTry:
                profile.cache = request.POST["res1"]
                profile.save()
            else:
                t = request.POST.get("res2", False)
                if t == False:
                    raise Exception()
        except:
            context["second1"] = (datetime.timedelta(seconds = profile.remainingTime) -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None))).seconds
            return render(request, 'myapp_RC/question.html',context)
        
    profile.accuracy = round((profile.correctanswers/(profile.quesno))*100,2)
    profile.save()

    # Passing timer
    context["second1"] = (datetime.timedelta(seconds = profile.remainingTime) -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None))).seconds     
    
    # Lifeline 3 availability
    if  profile.quesno > 1 and profile.lifeline3_status == False and profile.lifeline3_used == False:
        profile.lifeline3_status = True
    
    # if second attempt to the question
    if profile.isFirstTry == False :
        context["resp1"] = User_Response.objects.filter(user = ruser, user_profile = profile, quetionID = qList[0], isSimpleQuestion = False).first().response1
    
    # if user clicked lifeline 1 button
    if profile.lifeline1_using == True:
        givenAns = request.POST["res1"]
        profile.lifeline1_status = False  # To disable Simple Question button
        profile.simpleQuestionUsed = True 
        context["easyQuestion"] = False
        profile.lifeline1_using = False
        profile.plusmrks = 4
        profile.minusmrks = 0
        currQuest = EasyQuestion.objects.get(easyquestion_no = profile.lifeline1_question_id)
        if User_Response.objects.filter(user_profile = profile, quetionID = currQuest.easyquestion_no, response1 = givenAns, user = profile.user, isSimpleQuestion = True).exists():
            pass
        else:
            tempSol = User_Response(user_profile = profile, quetionID = currQuest.easyquestion_no, response1 = givenAns, user = profile.user, isSimpleQuestion = True)
            tempSol.save()
        
        # Different marking scheme
        if str(givenAns) == str(currQuest.easyanswer):
            profile.marks += 4
            profile.correctanswers+=1
        else:
            profile.marks -= 4
        
        profile.quesno += 1
        profile.questionIndexList = str(qList[1:])
        profile.isFirstTry = True
        profile.save()
        request.method = "GET"
        return QuestionView(request)
    
    # If timer over
    if profile.quesno == 30 or profile.remainingTime == 0:
        profile.logoutTime = datetime.datetime.now()
        profile.save()
        return redirect('Result')
    
    # Marking scheme
    context['plusmrks'] = profile.plusmrks
    context['minusmrks'] = profile.minusmrks

    # Normal POST request
    if request.method == "POST" :  
        qList = eval(profile.questionIndexList) # Question List

        if profile.isFirstTry:
            profile.plusmrks = 4
            profile.minusmrks = 0
            givenAns = request.POST["res1"]
            
            # Taking most recent response to avoid error primarily during testing,
            # where same user has multiple responses to same question
            if User_Response.objects.filter(user_profile = profile, quetionID = qList[0], response1 = givenAns, user = profile.user, isSimpleQuestion = False).exists() == False:
                tempSol = User_Response(user_profile = profile, quetionID = qList[0], response1 = givenAns, user = profile.user, isSimpleQuestion = False)
                tempSol.save()
            
            # Handling reload
            if profile.cacheAnswer != int(givenAns):
                profile.cacheAnswer = int(givenAns)

                # Marking
                if str(givenAns) == str(currQues.answer):

                    # For LL2
                    if profile.lifeline2_status and profile.lifeline2_checked == False:
                        profile.lifeline2_checked = True
                        profile.lifeline2_status = False
                        profile.remainingTime += 300
                        profile.lifeline2_secondattempt = False
                    
                    profile.correctanswers += 1
                    profile.marks += 4
                    profile.quesno += 1
                    profile.isFirstTry = True
                    
                    # Traversing question list
                    profile.questionIndexList = str(qList[1:])
                    
                    # LL1 fuel
                    if profile.lifeline1_count < 3 :
                        profile.lifeline1_count += 1
                
                else: # First attempt was wrong answer
                    if profile.lifeline2_status and profile.lifeline2_checked == False:
                        profile.remainingTime -= 120 
                        profile.lifeline2_secondattempt = True
                    profile.plusmrks = 2
                    profile.minusmrks = -2   
                    profile.isFirstTry = False  
                    profile.save()

        # Second attempt
        elif profile.isFirstTry == False:
            givenAns = request.POST["res2"]

            # Get user response containing response 1
            tempSol = User_Response.objects.filter(user = ruser, user_profile = profile, quetionID = qList[0], isSimpleQuestion = False).first()
            tempSol.response2 = givenAns
            tempSol.save()

            # Marking scheme
            profile.plusmrks = 4
            profile.minusmrks = 0
            
            # Correct answer
            if str(givenAns) == str(currQues.answer):
                if profile.lifeline2_status and profile.lifeline2_checked == False:
                    profile.lifeline2_checked = True
                    profile.lifeline2_status = False
                    profile.remainingTime += 300
                    profile.lifeline2_secondattempt = False
                profile.marks += 2
                profile.correctanswers += 1
                if profile.lifeline1_count < 3 :
                        profile.lifeline1_count += 1

            else: # Wrong answer
                if profile.lifeline2_status and profile.lifeline2_checked == False:
                    profile.lifeline2_checked = True
                    profile.lifeline2_status = False
                    profile.remainingTime -= 180
                    profile.lifeline2_secondattempt = False
                profile.marks -= 2
            
            profile.quesno += 1
            profile.isFirstTry = True
            qList = eval(profile.questionIndexList)
            profile.questionIndexList = str(qList[1:])
        
        profile.save()
        request.method = "GET"
        return QuestionView(request)
    return render(request, 'myapp_RC/question.html', context)

def leaderboard(request) :
    context = {}

    # Junior users
    context["usersjunior"] = list(Profile.objects.filter(category = True).order_by('marks',"remainingTime","accuracy").reverse())

    # Senior users
    context["userssenior"] = list(Profile.objects.filter(category = False).order_by('marks',"remainingTime", "accuracy").reverse())

    # All Users
    # context["users"] = list(Profile.objects.filter(category = True).order_by('marks',"remainingTime").reverse())

    return render(request, 'myapp_RC/leaderboard.html', context)

@login_required(login_url='SignIn')
def result(request):
    try:
        context = {}
        ruser = request.user
        profile = Profile.objects.get(user=ruser)
        context["profile"] = profile

        # Sorting based on marks
        context["users"] = list(Profile.objects.filter(category = bool(profile.category)).order_by('marks', 'remainingTime',"accuracy").reverse())
        profile.user_rank = context["users"].index(profile) + 1

        # Store logouttime in case of accidental logout
        profile.logoutTime = datetime.datetime.now()
        
        #  Extra data to be displayed
        profile.accuracy = round((profile.correctanswers/(profile.quesno))*100,2)
        context["q_correct"] = profile.accuracy
        if profile.remainingTime >= 2300:
            profile.remainingTime = 0
        context["timetaken"] = round(
            ((1800 - profile.remainingTime)/1800) * 100, 2)
        context["totalques"] = profile.quesno - 1
        profile.save()
        logout(request)
    except:
        return redirect('SignIn')
    return render(request, 'myapp_RC/result.html', context)


@login_required(login_url = 'SignIn')
def lifelineone(request):
    context = { }
    ruser = request.user
    profile = Profile.objects.get(user = ruser)

    # Changing LL1 fields
    profile.lifeline1_using = True
    profile.lifeline1_count = 0
    profile.lifeline1_status = False
    
    # Marking scheme
    profile.plusmrks = 4
    profile.minusmrks = -4

    # Passing data
    context['plusmrks'] = profile.plusmrks
    context['minusmrks'] = profile.minusmrks
    qList = eval(profile.questionIndexList)
    context["easyQuestion"] = True
    context["isSimpleQuestion"] = profile.simpleQuestionUsed
    context['currquestNum'] = profile.quesno
    
    # Easy question to display
    currQuest = EasyQuestion.objects.get(easyquestion_no = profile.lifeline1_question_id)
    context["currquest"] = currQuest.easyquestion
    context["profile"] = profile

    # Timer
    context["second1"] = (datetime.timedelta(seconds = profile.remainingTime) -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None))).seconds 
    profile.startTime = datetime.datetime.now()
    profile.remainingTime = context["second1"]
       
    # Timer over
    if profile.quesno == 30 or profile.remainingTime == 0 :
        profile.logoutTime = datetime.datetime.now()
        profile.save()
        return redirect('Result')
    
    # No second attempt
    profile.isFirstTry = True
    profile.save()
    return render(request, 'myapp_RC/question.html', context)

def lifeLine3(request):
    ruser = request.user
    profile = Profile.objects.get(user = ruser)

    # Changing LL3 fields
    profile.lifeline3_status = False
    profile.lifeline3_used = True
    profile.save()

    try :
        profile.lifeline3_used = True
        profile.save()
        if request.method == "GET":
            userQuery = request.GET["question"]
            
            # Get non-depleated keys
            allKeys = chatGPTLifeLine.objects.all()
            allKeys2 = chatGPTLifeLine.objects.filter(isDepleted = False)

            # Error if no keys found
            if len(allKeys2) == 0:
                return JsonResponse({'question': {userQuery},'answer': "Somethingwentwrong"})
            isproblem = True

            # Deplete 3 times used keys + dont use just used key
            # currentTime = time.time()
            for key in allKeys2:
                # print(f"Key last used {currentTime - key.lastUsed} seconds ago")
                # print(f"{currentTime} - {key.lastUsed} = {currentTime - key.lastUsed}")
                if key.numUsed < 3:
                    isproblem = False
                    key.numUsed += 1
                    key.lastUsed = time.time()
                    key.save()
                    break
                else:
                    key.isDepleted = True
                    key.save()

            # Error
            if isproblem:
                return JsonResponse({'question': {userQuery},'answer': "Somethingwentwrong"})
            
            # Get Chat GPT Answer
            answerResp = GPT_Link(userQuery, key= key)
            return JsonResponse({'question': userQuery,'answer': answerResp})
    except :
        return JsonResponse({'question': {userQuery},'answer': "Somethingwentwrong"})

def GPT_Link(message, key):
    URL = "https://api.openai.com/v1/chat/completions"

    payload = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": message}],
    "temperature" : 1.0,
    "top_p":1.0,
    "n" : 1,
    "stream": False,
    "presence_penalty":0,
    "frequency_penalty":0,
    }

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {key}"
    }

    response = requests.post(URL, headers=headers, json=payload, stream=False)
    return (json.loads(response.content)["choices"][0]['message']['content'])

@login_required(login_url = 'SignIn')
def lifeline2(request):
    
    # Changing LL2 fields on AJAX request
    ruser = request.user
    profile = Profile.objects.get(user = ruser)
    profile.lifeline2_status = True
    profile.lifeline2_superstatus = False
    profile.save()
    return JsonResponse({'success':'True'})
       
# In case of emergency and accidental logout
def webadmin(request) :
    if request.method == 'POST':
        superusername = request.POST['superusername']
        superpwd = request.POST['pass1']

        username = request.POST['username']
        password = request.POST['pass']

        superuser = authenticate(username = superusername, password = superpwd)
        user = authenticate(username = username, password = password)

        if superuser.is_superuser and user is not None:
            profile = Profile.objects.get(user = user)
            profile.remainingTime += int(request.POST['tabs'])
            profile.newlogin = False
            profile.save()

            messages.success(request, "Updated")
            return render(request, "myapp_RC/signin.html")

        else:
            messages.error(request, "Bad Credentials")
            return render(request, "myapp_RC/signin.html")
        
    return render (request, "myapp_RC/webadmin.html")

# Save timer with AJAX function in backend
@csrf_exempt
def savetimer(request) :
    if request.method == 'POST':
        context = {}
        ruser = request.user
        profile = Profile.objects.get(user = ruser)
        context["second1"] = (datetime.timedelta(seconds = profile.remainingTime) -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None))).seconds
        profile.startTime = datetime.datetime.now()
        profile.remainingTime = context["second1"]
        profile.save()
        return JsonResponse({'success':'True'})
    
# Error Handlers
def error_view(request, exception=404):
    return render(request, 'myapp_RC/error.html')

def error_500(request):
    return render(request, 'myapp_RC/error.html')