from django.urls import path
from . import views
from rest_framework import routers
from django.conf.urls import url, include


router = routers.DefaultRouter()
router.register(r'Visitor', views.VisitorViewSet)
router.register(r'Host', views.HostViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('logbook/', views.logbook, name='logbook'),
    url(r'^statusupdate/(?P<id>\d+)/', views.statusupdate, name='statusupdate'),
    path('addressbook/', views.addressbook, name='addressbook'),
    path('locations/', views.locations, name='locations'),
    path('analytics/', views.analytics, name='analytics'),
    path('colleagues/', views.colleagues, name='colleagues'),
    path('addnewvisit/', views.addnewvisit, name='addnewvisit'),
    path('addnewhost/', views.addnewhost, name='addnewhost'),
    path('api/data/HostView/', views.HostView.as_view()),
    path('api/data/VisitorView/', views.VisitorView.as_view()),
    url(r'^logbook/delselected/(?:id=(?P<id>\d+)/)?$', views.delselected, name='delselected'),
]