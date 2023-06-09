from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Basic User data
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_rank = models.IntegerField(default=0,null=True)
    questionIndexList = models.TextField(default="[-1]")
    correctanswers = models.IntegerField(default=0)
    quesno = models.IntegerField(default=1)
    mob_no = models.CharField(max_length=12)
    isFirstTry = models.BooleanField(default = True)
    isTimeOut = models.BooleanField(default = False)
    startTime = models.DateTimeField(null = True)
    tempTime = models.DateTimeField(null = True)
    logoutTime = models.DateTimeField(null=True)
    newlogin = models.BooleanField(default = False)
    category = models.BooleanField(default=True) #True if Junior, False if Senior
    remainingTime = models.IntegerField(default = 1800)

    # Marking scheme
    plusmrks = models.IntegerField(default = 4)
    minusmrks = models.IntegerField(default = 0)

    # For Result page
    display_name = models.CharField(max_length=1000, default="", null=True)
    marks = models.IntegerField(default=0)
    accuracy = models.FloatField(default=0)
    cache = models.IntegerField(default=0)
    cacheAnswer = models.IntegerField(default=-1)

    # Lifeline 1
    lifeline1_count = models.IntegerField(default=0)
    lifeline1_status = models.BooleanField(default=False)
    lifeline1_using = models.BooleanField(default=False)
    lifeline1_question_id = models.IntegerField(default=0)
    simpleQuestionUsed = models.BooleanField(default=False)

    # Lifeline 2
    lifeline2_superstatus = models.BooleanField(default = True)
    lifeline2_timeout = models.BooleanField(default = False)
    lifeline2_status = models.BooleanField(default = False)
    lifeline2_checked = models.BooleanField(default = False)
    lifeline2_secondattempt = models.BooleanField(default = False)

    # Lifeline 3
    lifeline3_status = models.BooleanField(default = False)
    lifeline3_used = models.BooleanField(default = False)

    def __str__(self):
        return self.user.username
    

class Question(models.Model):
    question_no = models.IntegerField()    
    question=models.CharField(max_length=1000)
    answer=models.IntegerField(default=-1)
    is_junior = models.BooleanField(default = True)
    
    def __str__(self):
        return self.question


class User_Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=None)
    user_profile= models.ForeignKey(Profile, on_delete = models.CASCADE,null=True)
    quetionID = models.IntegerField(default=-1)
    response1 = models.CharField(null = True,max_length=1000)
    response2 = models.CharField(null = True,max_length=1000)

    isSimpleQuestion = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class EasyQuestion(models.Model):
    easyquestion_no = models.IntegerField()    
    easyquestion=models.CharField(max_length=1000)
    easyanswer=models.IntegerField(default=-1)
    
    def __str__(self):
        return self.easyquestion
    

class chatGPTLifeLine(models.Model):
    key = models.CharField(max_length=1000)
    numUsed = models.IntegerField(default=0)
    lastUsed = models.FloatField(default= 1700000000.213593)
    isDepleted = models.BooleanField(default=False)
        
    def __str__(self):
        return self.key