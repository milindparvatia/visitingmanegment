from .models import Visitor
from django.conf.urls import url
from django.urls import path
from . import views, url_settings
from rest_framework import routers
from django.conf.urls import url, include

urlpatterns = [
    path('logbook/', views.logbook, name='logbook'),
    path('addressbook/', views.addressbook, name='addressbook'),
    url(r'^addressbook/(?P<id>\d+)/edit/$',
        views.addressbookedit, name='addressbookedit'),
    url(r'^addressbook/(?P<id>\d+)/$',
        views.addressbookdetail, name='addressbookdetail'),
    url(r'^delselectedaddress/(?:id=(?P<id>\d+)/)?$',
        views.delselectedaddress, name='delselectedaddress'),
    path('locations/', views.locations, name='locations'),
    url(r'^locations/(?P<id>\d+)/$', views.editlocations, name='editlocations'),
    path('analytics/', views.analytics, name='analytics'),
    path('colleagues/', views.colleagues, name='colleagues'),
    path('addnewvisit/', views.addnewvisit, name='addnewvisit'),
    path(r'addmultipleMeeting/',
         views.addmultipleMeeting, name='addmultipleMeeting'),
    url(r'addmultiplevisit/(?P<id>\d+)/$',
        views.addmultiplevisit, name='addmultiplevisit'),
    url(r'^useoldvisit/(?P<id>\d+)/$', views.use_old_visit, name='useoldvisit'),
    path('addnewhost/', views.addnewhost, name='addnewhost'),
    path('search_visitor/', views.search_visitor, name='search_visitor'),
    path('searchlist/', views.searchlist, name='searchslist'),
    path('search_list/', views.search_list, name='searchs_list'),
    url(r'^statusupdate/(?P<id>\d+)/', views.statusupdate, name='statusupdate'),
    url(r'^delselected/(?:id=(?P<id>\d+)/)?$',
        views.delselected, name='delselected'),
    url(r'^colleagues/(?P<id>\d+)/$', views.viewuser, name='viewuser'),
    url(r'^colleagues/(?P<id>\d+)/edituser/$', views.edituser, name='edituser'),
    url(r'^colleagues/(?P<id>\d+)/password/$', views.password, name='password'),
    url(r'^search/', include('haystack.urls')),
    url(r'^addselected/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        views.addselected, name='addselected'),
    path('settings/', include('app.url_settings')),
]
