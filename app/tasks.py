from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail


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
