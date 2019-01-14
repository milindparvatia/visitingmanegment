from app.models import Visitor,Host, Map
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class VisitorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Visitor
        fields = ('url', 'id', 'first_name', 'last_name', 'email', 'mobile', 'comment','company_name','licenseplate','about','visiting')

class HostSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="host-detail")

    class Meta:
        model = Host
        fields = ('url', 'id', 'first_name', 'last_name', 'email', 'mobile', 'comment')

class MAPSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Map
        fields = ('url', 'id', 'loc', 'lon', 'lat', 'name')

class HostSerializer(ModelSerializer):
    class Meta:
        model = Host
        fields = [
            "id",
            "full_name",
            "email",
            "mobile",
            "comment"
        ]

class VisitorSerializer(ModelSerializer):
    class Meta:
        model = Visitor
        fields = [
            "id",
            "full_name",
            'status',
            "company_name",
            "email",
            "mobile",
            "licenseplate",
            "about",
            "comment",
            "visiting",
            'date',
            'start_time',
            'end_time'
        ]