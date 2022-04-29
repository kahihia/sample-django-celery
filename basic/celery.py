from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basic.settings')
app = Celery('basic')
app.config_from_object('django.conf.settings', namespace='CELERY')

app.conf.beat_schedule = {
    'remove-expired-OTPTokens' : {
        'task': 'account.tasks.remove_expired_OTPTokens',
        'schedule': crontab(hour=15, minute=42),
        'args': ('Scheduled task done...',),
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
