from app.models import Visitor,Visit,Host
from rest_framework.serializers import ModelSerializer

# class VisitorSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Visitor
#         fields = ('url', 'first_name', 'last_name', 'email', 'mobile', 'comment','company_name','licenseplate','about','visiting')


# class VisitSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Visit
#         fields = ('url','visitor','Host','visit','invite_reason')

# class HostSerializer(serializers.HyperlinkedModelSerializer):
#     url = serializers.HyperlinkedIdentityField(view_name="host-detail")

#     class Meta:
#         model = Host
#         fields = ('url', 'first_name', 'last_name', 'email', 'mobile', 'comment')

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

class VisitSerializer(ModelSerializer):
    class Meta:
        model = Visit
        fields = [
            "visitor",
            "Host",
            "visit",
            "invite_reason"
        ]