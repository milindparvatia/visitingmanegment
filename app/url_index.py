from django.urls import path
from . import views
from rest_framework import routers
from django.conf.urls import url, include
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

router = routers.DefaultRouter()
router.register(r'User', views.UserViewSet)
router.register(r'Visitor', views.VisitorViewSet)
router.register(r'Host', views.HostViewSet)
router.register(r'Map', views.MAPViewSet)
router.register(r'Meeting', views.MeetingViewSet)

urlpatterns = [
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include_docs_urls(title='Visitor APIs Doc', public=False)),
    url(r'^api/', include(router.urls)),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('addnewlocations/', views.addnewlocations, name='addnewlocations'),
]
