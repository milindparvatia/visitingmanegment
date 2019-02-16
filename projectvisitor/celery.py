from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# app = Celery('app',
#              broker='amqp://pcsgopbw:sj_GnV8BOtaW9QTOgreZ-eTr1zCyvCoB@llama.rmq.cloudamqp.com/pcsgopbw',
#              backend='redis://192.168.99.100:32774',
#              include=['app.tasks'])

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectvisitor.settings')

app = Celery('projectvisitor')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
