from django.db import models
from django import forms
import datetime

class Map(models.Model):
    loc = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    lon = models.FloatField()
    lat = models.FloatField()

    def __str__(self):
        return self.name

class Host(models.Model):
    full_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=20)
    mobile = models.IntegerField()
    comment = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.full_name

STATUS_CHOICES = (
   ('expected', 'expected'),
   ('check-in', 'check-in'),
   ('check-out', 'check-out')
)

class Visitor(models.Model):
    full_name = models.CharField(max_length=30)
    company_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    mobile = models.CharField(max_length=20)
    licenseplate = models.CharField(max_length=20)
    about = models.CharField(max_length=50, null=True)
    comment = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.full_name

class Meeting(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE,related_name='relateds')
    host = models.ManyToManyField(Host,related_name='relateds')
    status = models.CharField(choices=STATUS_CHOICES, blank=False, max_length=128)
    location = models.ForeignKey(Map, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    start_time = models.TimeField()
    end_time = models.TimeField()