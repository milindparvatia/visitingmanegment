from django.urls import path
from . import views, url_settings, url_profile
from rest_framework import routers
from django.conf.urls import url, include

urlpatterns = [
    path('logbook/', views.logbook, name='logbook'),
    url(r'^statusupdate/(?P<id>\d+)/', views.statusupdate, name='statusupdate'),
    path('addressbook/', views.addressbook, name='addressbook'),
    path('locations/', views.locations, name='locations'),
    path('analytics/', views.analytics, name='analytics'),
    path('colleagues/', views.colleagues, name='colleagues'),
    path('addnewvisit/', views.addnewvisit, name='addnewvisit'),
    path('addnewhost/', views.addnewhost, name='addnewhost'),
    url(r'^logbook/delselected/(?:id=(?P<id>\d+)/)?$',
        views.delselected, name='delselected'),
    path('settings/', include('app.url_settings')),
    path('profile/', include('app.url_profile')),
]
