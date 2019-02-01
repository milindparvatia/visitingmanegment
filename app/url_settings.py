from django.urls import path
from . import views
from rest_framework import routers
from django.conf.urls import url, include

urlpatterns = [
    path('company/', views.settings_general_company, name='company'),
    path('user-management/', views.settings_general_management, name='user'),
    path('user-rights/', views.settings_general_rights, name='rights'),
    path('billing-plan/', views.settings_other_billing, name='billing'),
    path('building-security/', views.settings_other_buildingsecurity,
         name='buildingsecurity'),
    path('integrations/', views.settings_other_integrations, name='integrations'),
    path('privacy/', views.settings_other_privacy, name='privacy'),
    path('kiosk_list/', views.settings_visitslist_kiosklist, name='kiosklist'),
    path('logbooksettings/', views.settings_visitslist_logbook,
         name='logbooksettings'),
    path('printer/', views.settings_visitslist_printer, name='printer'),
    path('notifications/', views.settings_visitslist_notifications,
         name='notifications'),
]
