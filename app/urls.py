from .models import Visitor
from django.conf.urls import url
from django.urls import path
from . import views, url_settings, url_profile
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
    path('analytics/', views.analytics, name='analytics'),
    path('colleagues/', views.colleagues, name='colleagues'),
    path('addnewvisit/', views.addnewvisit, name='addnewvisit'),
    url(r'^useoldvisit/(?P<id>\d+)/', views.use_old_visit, name='useoldvisit'),
    path('addnewhost/', views.addnewhost, name='addnewhost'),
    path('search_visitor/', views.search_visitor, name='searchvisitor'),
    path('searchlist/', views.searchlist, name='searchslist'),
    path('search_list/', views.search_list, name='searchs_list'),
    url(r'^statusupdate/(?P<id>\d+)/', views.statusupdate, name='statusupdate'),
    url(r'^delselected/(?:id=(?P<id>\d+)/)?$',
        views.delselected, name='delselected'),
    path('settings/', include('app.url_settings')),
    path('profile/', include('app.url_profile')),
    url(r'^search/', include('haystack.urls')),
]
