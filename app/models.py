from django.db import models
from django import forms
import datetime

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
    status = models.CharField(choices=STATUS_CHOICES, blank=False, max_length=128)
    company_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    mobile = models.IntegerField()
    licenseplate = models.IntegerField(null=True)
    about = models.CharField(max_length=50, null=True)
    comment = models.CharField(max_length=100, null=True)
    visiting = models.ManyToManyField(Host,related_name='relateds')
    date = models.DateField(default=datetime.date.today)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return self.full_name