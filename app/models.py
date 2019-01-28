import datetime
from django import forms
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import pre_save


class Map(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loc = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    lon = models.FloatField()
    lat = models.FloatField()

    def __str__(self):
        return self.name
        return self.slug


def pre_save_slug_receiver(sender, instance, *args, **kwargs):
    slug = slugify(instance.name)
    exists = Map.objects.filter(slug=slug).exists()
    if exists:
        slug = "%s-%s" % (slug, instance.id)
    instance.slug = slug


pre_save.connect(pre_save_slug_receiver, sender=Map)


class Host(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visitor = models.ForeignKey(
        Visitor, on_delete=models.CASCADE, related_name='relateds')
    host = models.ManyToManyField(Host, related_name='relateds')
    status = models.CharField(choices=STATUS_CHOICES,
                              blank=False, max_length=128)
    location = models.ForeignKey(Map, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    start_time = models.TimeField()
    end_time = models.TimeField()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=20, null=True)
    mobile = models.CharField(max_length=20, null=True)
    licenseplate = models.CharField(max_length=20, null=True)
    about = models.CharField(max_length=50, null=True)
    comment = models.CharField(max_length=100, null=True)
    location = models.ForeignKey(Map, on_delete=models.CASCADE, null=True)
    profile_pic = models.ImageField(upload_to='media_data', blank=True)

# def pre_save_user_receiver(sender, instance, *args, **kwargs):
#     user = slugify(instance.name)
#     exists = Map.objects.filter(slug=slug).exists()
#     if exists:
#         slug = "%s-%s" % (slug, instance.id)
#     instance.slug = slug


# pre_save.connect(pre_save_user_receiver, sender=User)
