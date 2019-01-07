from app.models import Visitor,Host
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class VisitorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Visitor
        fields = ('url', 'first_name', 'last_name', 'email', 'mobile', 'comment','company_name','licenseplate','about','visiting')

class HostSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="host-detail")

    class Meta:
        model = Host
        fields = ('url', 'first_name', 'last_name', 'email', 'mobile', 'comment')

class HostSerializer(ModelSerializer):
    class Meta:
        model = Host
        fields = [
            "full_name",
            "email",
            "mobile",
            "comment"
        ]

class VisitorSerializer(ModelSerializer):
    class Meta:
        model = Visitor
        fields = [
            "full_name",
            "company_name",
            "email",
            "mobile",
            "licenseplate",
            "about",
            "comment",
            "visiting"
        ]