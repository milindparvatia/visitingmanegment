from django.contrib import admin
from app.models import Visitor, Host, Meeting, Map
from django import forms

admin.site.register(Visitor)
admin.site.register(Host)
admin.site.register(Meeting)
admin.site.register(Map)
