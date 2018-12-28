from django.urls import path
from . import views
from rest_framework import routers
from django.conf.urls import url, include
# from .views import CompanyListView


# router = routers.DefaultRouter()
# router.register(r'Visitor', views.VisitorView.as_view())
# router.register(r'Visit', views.VisitView.as_view())
# router.register(r'Host', views.HostView.as_view())

urlpatterns = [
    # url(r'^/api/data/', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('logbook/', views.logbook, name='logbook'),
    # path('api/', CompanyListView.as_view()),
    path('addressbook/', views.addressbook, name='addressbook'),
    path('locations/', views.locations, name='locations'),
    path('analytics/', views.analytics, name='analytics'),
    path('colleagues/', views.colleagues, name='colleagues'),
    path('addnewvisit/', views.addnewvisit, name='addnewvisit'),
    path('addnewhost/', views.addnewhost, name='addnewhost'),
    path('api/data/HostView/', views.HostView.as_view()),
    path('api/data/VisitorView/', views.VisitorView.as_view()),
    path('api/data/VisitView/', views.VisitView.as_view()),
]