from django.urls import path
from . import views
from rest_framework import routers
from django.conf.urls import url, include

urlpatterns = [
    path('view/', views.view, name='view'),
    path('edituser/', views.edituser, name='edituser'),
    path('password/', views.password, name='password'),
]
