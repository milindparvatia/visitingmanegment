from django.urls import path
from . import views
from rest_framework import routers
from django.conf.urls import url, include

urlpatterns = [
    path('company/', views.settings, name='settings'),
]
