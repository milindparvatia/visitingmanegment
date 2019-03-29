from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from push_notifications.models import APNSDevice


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def sendmail(subject, message, sender_email, receipient_email):
    return send_mail(subject, message, sender_email, [receipient_email], fail_silently=False)


@shared_task
def sendnotification(user_email, meeting_id, status, visitor_name, visitor_profile_pic):
    print("1")
    device = APNSDevice.objects.filter(name=user_email)
    return device.send_message("visitor "+visitor_name+" is arrived", thread_id="1",
                               extra={
                                   "notification_type": "1",
                                   "meeting_id": "1",
                                   "status": status,
                                   "visitor_name": visitor_name,
                                   "visitor_profile_pic": visitor_profile_pic
                               })


@shared_task
def sendassistant(user_email):
    print("1")
    device = APNSDevice.objects.filter(name=user_email)
    return device.send_message("Your assistance is requiered at Kiosk", thread_id="1",
                               extra={
                                   "notification_type": "1",
                               })
