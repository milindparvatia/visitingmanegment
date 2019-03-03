from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from app.models import *
from django.contrib.auth import get_user_model
User = get_user_model()


class VisitorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Visitor
        fields = ('url', 'id', 'full_name', 'email', 'mobile',
                  'comment', 'company_name', 'licenseplate', 'about', 'user')


class TheCompanySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TheCompany
        fields = ('url', 'id', 'name', 'location')


class MeetingSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="meeting-detail")

    class Meta:
        model = Meeting
        fields = ('url', 'id', 'status', 'visitor', 'host',
                  'location', 'date', 'start_time', 'end_time', 'user')
        depth = 1


class MAPSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="map-detail")

    class Meta:
        model = Map
        fields = ('url', 'id', 'loc', 'lon', 'lat', 'name', 'slug', 'user')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'is_active', 'last_login', 'date_joined',
                  'password', 'email', 'groups')


# class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ('url', 'id', 'user', 'hosts', 'company_name', 'comp', 'mobile', 'location',
#                   'licenseplate', 'about', 'comment', 'profile_pic')
