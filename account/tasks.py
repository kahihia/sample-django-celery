from __future__ import absolute_import, unicode_literals
from celery import shared_task

from account.models import OTPToken


@shared_task(bind=True)
def remove_expired_OTPTokens(self, data):
    print(data)
    tokens = OTPToken.objects.all()
    for token in tokens:
        if token.is_expired:
            token.delete()

    