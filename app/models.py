import django
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import datetime
from datetime import timedelta
from django.conf import settings
from django import forms
from django.db import models
from django.utils.text import slugify
from django.core.validators import RegexValidator


class Map(models.Model):
    loc = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    lon = models.FloatField()
    lat = models.FloatField()

    def __str__(self):
        return self.slug


def post_save_slug_receiver(sender, instance, *args, **kwargs):
    slug = slugify(instance.name)
    exists = Map.objects.filter(slug=slug).exists()
    randomstring = BaseUserManager().make_random_password()
    if exists:
        slug = "%s-%s" % (slug, randomstring)
    instance.slug = slug


pre_save.connect(post_save_slug_receiver, sender=Map)


class TheCompany(models.Model):
    name = models.CharField(max_length=30)
    location = models.ManyToManyField(
        Map, related_name='related_maps', blank=True, default='')

    def __str__(self):
        return self.name


class MyUserManager(BaseUserManager):
    def create_user(self, email, full_name, mobile, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            mobile=mobile,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, mobile, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            full_name=full_name,
            mobile=mobile,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


USER_TYPE_CHOICES = (
    ('1', 'secretary'),
    ('2', 'receptionist'),
    ('3', 'admin'),
)


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    user_type = models.CharField(
        choices=USER_TYPE_CHOICES, max_length=20, default='')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    full_name = models.CharField(max_length=50, blank=True, default='')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    mobile = models.CharField(
        validators=[phone_regex], max_length=17, blank=True)
    licenseplate = models.CharField(max_length=20, blank=True, default='')
    about = models.CharField(max_length=50, blank=True, default='')
    comment = models.CharField(max_length=100, blank=True, default='')
    profile_pic = models.ImageField(
        upload_to='user_data',  default='media_data/profile-pic.png')
    our_company = models.ForeignKey(
        TheCompany, on_delete=models.CASCADE, null=True, default='')
    user_location = models.ManyToManyField(
        Map, related_name='related_userlocation', default='')

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'mobile']

    def __str__(self):
        return "Name: %s, Phone: %s" % (self.full_name, self.mobile)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Delivery(models.Model):
    our_company = models.ForeignKey(
        TheCompany, on_delete=models.CASCADE, null=True, default='')
    Deliverytype = models.CharField(max_length=30)
    which_user = models.ManyToManyField(
        User, related_name='related_userdelivery', default='')
    which_date = models.DateField(default=django.utils.timezone.now)
    which_time = models.TimeField()

    def __str__(self):
        return self.which_date


class Visitor(models.Model):
    our_company = models.ForeignKey(
        TheCompany, on_delete=models.CASCADE, null=True, default='')
    full_name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    mobile = models.CharField(
        validators=[phone_regex], max_length=17, blank=True)
    licenseplate = models.CharField(max_length=20, blank=True, default='')
    about = models.CharField(max_length=50, blank=True, default='')
    comment = models.CharField(max_length=100, blank=True, default='')
    profile_pic = models.ImageField(
        upload_to='visitor_data', default='media_data/profile-pic.png')

    def __str__(self):
        return "Name: %s, Phone: %s" % (self.full_name, self.mobile)


STATUS_CHOICES = (
    ('expected', 'expected'),
    ('check-in', 'check-in'),
    ('check-out', 'check-out')
)

COUNTER_CHOICES = (
    ('by-kiosk', 'by-kiosk'),
    ('by-dashboard', 'by-dashboard'),
    ('not-check-in', 'not-check-in')
)

TIMER_CHOICES = (
    ('5', '5 min'),
    ('10', '10 min'),
    ('0', 'let them in')
)


class Meeting(models.Model):
    our_company = models.ForeignKey(
        TheCompany, on_delete=models.CASCADE, null=True, default='')
    visitor = models.ForeignKey(
        Visitor, related_name='related_visitor', on_delete=models.CASCADE, null=True, default='')
    host = models.ManyToManyField(
        User, related_name='related_host', blank=True, default='')
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)
    counter = models.CharField(
        choices=COUNTER_CHOICES, max_length=15, default='by-dashboard')
    timer = models.CharField(
        choices=TIMER_CHOICES, max_length=15, default='')
    pre_registered = models.BooleanField(default=True)
    location = models.ForeignKey(Map, on_delete=models.CASCADE)
    date = models.DateField(
        default=django.utils.timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
