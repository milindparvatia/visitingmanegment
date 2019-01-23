from app.models import Visitor, Host, Map, Meeting
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class VisitorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Visitor
        fields = ('url', 'id', 'full_name', 'email', 'mobile',
                  'comment', 'company_name', 'licenseplate', 'about')


class HostSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="host-detail")

    class Meta:
        model = Host
        fields = ('url', 'id', 'full_name', 'email', 'mobile', 'comment')


class MeetingSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="meeting-detail")

    class Meta:
        model = Meeting
        fields = ('url', 'id', 'status', 'visitor', 'host',
                  'location', 'date', 'start_time', 'end_time')


class MAPSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="map-detail")

    class Meta:
        model = Map
        fields = ('url', 'id', 'loc', 'lon', 'lat', 'name', 'slug')
