from django.contrib.auth.models import User
from app.models import Visitor, Host, Map, Meeting, UserProfile
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class VisitorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Visitor
        fields = ('url', 'id', 'full_name', 'email', 'mobile',
                  'comment', 'company_name', 'licenseplate', 'about', 'user')


class HostSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="host-detail")

    class Meta:
        model = Host
        fields = ('url', 'id', 'full_name', 'email',
                  'mobile', 'comment', 'user')


class MeetingSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="meeting-detail")

    class Meta:
        model = Meeting
        fields = ('url', 'id', 'status', 'visitor', 'host',
                  'location', 'date', 'start_time', 'end_time', 'user')


class MAPSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="map-detail")

    class Meta:
        model = Map
        fields = ('url', 'id', 'loc', 'lon', 'lat', 'name', 'slug', 'user')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'first_name', 'last_name', 'is_active', 'last_login', 'date_joined',
                  'username', 'password', 'email', 'groups')


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('url', 'user', 'company_name', 'mobile', 'location',
                  'licenseplate', 'about', 'comment', 'profile_pic')
