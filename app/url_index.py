from django.urls import path
from . import views
from rest_framework import routers
from django.conf.urls import url, include
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from push_notifications.api.rest_framework import APNSDeviceAuthorizedViewSet, GCMDeviceAuthorizedViewSet

router = routers.DefaultRouter()
router.register(r'User', views.UserViewSet)
router.register(r'Visitor', views.VisitorViewSet)
router.register(r'TheCompany', views.TheCompanyViewSet)
router.register(r'Map', views.MAPViewSet)
router.register(r'Meeting', views.MeetingViewSet)
router.register(r'Delivery', views.DeliveryViewSet)
router.register(r'device/apns', APNSDeviceAuthorizedViewSet)
router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)

schema_view = get_schema_view(title='Pastebin API')

urlpatterns = [
    url(r'^api/(?P<visitor_id>(\d+))/(?P<user_id>(\d+))/$',
        views.MeetingFilter.as_view()),
    path('user_added/', views.user_added, name='user_added'),
    path('ListUsers/', views.ListUsers.as_view()),
    path('Assistant/', views.AssistantApi.as_view()),
    path('schema/', schema_view),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include_docs_urls(title='Visitor APIs Doc', public=False)),
    url(r'^api/', include(router.urls)),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('addnewlocations/', views.addnewlocations, name='addnewlocations'),
]
