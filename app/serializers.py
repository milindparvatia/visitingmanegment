from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from app.models import *
from django.contrib.auth import get_user_model
User = get_user_model()


class VisitorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Visitor
        fields = ('url', 'id',  'our_company', 'full_name', 'email', 'mobile',
                  'comment', 'company_name', 'licenseplate', 'about', 'profile_pic')


class TheCompanySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TheCompany
        fields = ('url', 'id', 'name', 'location')


class MeetingSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="meeting-detail")

    class Meta:
        model = Meeting
        fields = ('url', 'id', 'status', 'visitor', 'counter', 'timer', 'pre_registered', 'host',
                  'location', 'date', 'start_time', 'end_time', 'our_company')
        depth = 1


class MAPSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="map-detail")

    class Meta:
        model = Map
        fields = ('url', 'id', 'loc', 'lon', 'lat', 'name', 'slug')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id',  'full_name', 'is_active', 'user_type', 'last_login', 'is_admin', 'email',
                  'mobile', 'licenseplate', 'about', 'comment', 'user_location', 'profile_pic', 'our_company')


class DeliverySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Delivery
        fields = ('url', 'id', 'our_company', 'Deliverytype',
                  'which_user', 'which_date', 'which_time')
