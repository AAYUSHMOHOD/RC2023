from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home, name = 'Login'),
    path('home/', views.home, name = 'Login'),
    path('signup/', views.signup, name = 'SignUp'),
    path('signin/', views.signin, name = 'SignIn'),
    path('signout/', views.signout, name = 'SignOut'),
    path('instruction/',views.instruction, name = 'Instruction'),
    path('question/', views.QuestionView, name = 'QuestionView1'),
    path('result', views.result, name = 'Result'),
    path('lifeline1/', views.lifelineone, name = 'lifeline1'),
    path('lifeline3/', views.lifeLine3, name = 'lifeline3'),
    path('lifeline2/', views.lifeline2, name = 'lifeline2'),
    path('leaderboard/', views.leaderboard, name = 'leaderboard'),
    path('webadmin/', views.webadmin, name = 'Admin'),
    path('savetimer/', views.savetimer, name = 'Savetimer'),
    path('error/', views.error_view, name = 'error'),
]