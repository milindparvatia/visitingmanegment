from django.db.models.signals import pre_save, post_save, m2m_changed
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import datetime
from django.conf import settings
from django import forms
from django.db import models
from django.utils.text import slugify


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


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    full_name = models.CharField(max_length=30, blank=True, default='')
    colleague = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='related_user', null=True, default='')
    mobile = models.CharField(max_length=20, blank=True, default='')
    licenseplate = models.CharField(max_length=20, blank=True, default='')
    about = models.CharField(max_length=50, blank=True, default='')
    comment = models.CharField(max_length=100, blank=True, default='')
    profile_pic = models.ImageField(
        upload_to='user_data',  default='media_data/profile-pic.png')
    our_company = models.ForeignKey(
        TheCompany, on_delete=models.CASCADE, null=True, default='')

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'mobile']

    def __str__(self):
        return self.email

    def __unicode__(self):
        return "{0}".format(self.full_name)

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
    licenseplate = models.CharField(max_length=20, blank=True, default='')
    about = models.CharField(max_length=50, blank=True, default='')
    comment = models.CharField(max_length=100, blank=True, default='')
    profile_pic = models.ImageField(
        upload_to='visitor_data', default='media_data/profile-pic.png')

    def __str__(self):
        return self.full_name


class Meeting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visitor = models.ForeignKey(
        Visitor, on_delete=models.CASCADE, related_name='related_visitor')
    host = models.ManyToManyField(
        User, related_name='related_host', blank=True, default='')
    status = models.CharField(choices=STATUS_CHOICES, max_length=128)
    location = models.ForeignKey(Map, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    start_time = models.TimeField()
    end_time = models.TimeField()


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     hosts = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='related_user', null=True, default='')
#     company_name = models.CharField(max_length=20, blank=True, default='')
#     mobile = models.CharField(max_length=20, blank=True, default='')
#     licenseplate = models.CharField(max_length=20, blank=True, default='')
#     about = models.CharField(max_length=50, blank=True, default='')
#     comment = models.CharField(max_length=100, blank=True, default='')
#     location = models.ForeignKey(
#         Map, on_delete=models.CASCADE, null=True, default='')
#     profile_pic = models.ImageField(
#         upload_to='user_data',  default='media_data/profile-pic.png')
#     comp = models.ForeignKey(
#         TheCompany, on_delete=models.CASCADE, null=True, default='')


# def pre_save_userprofile_receiver(sender, instance, *args, **kwargs):
#     user = instance.user
#     host = User.objects.filter(username=user)
#     print(host)
#     # exists = host.exists()
#     # if exists:
#     #     instance.hosts.set(host)


# pre_save.connect(pre_save_userprofile_receiver, sender=Map)

# class Host(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     full_name = models.CharField(max_length=30)
#     email = models.EmailField(max_length=20)
#     mobile = models.IntegerField()
#     comment = models.CharField(max_length=100, blank=True, default='')
#     profile_pic = models.ImageField(
#         upload_to='host_data', default='media_data/profile-pic.png')

#     def __str__(self):
#         return self.full_name
