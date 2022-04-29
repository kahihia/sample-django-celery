from django.dispatch import receiver
from django.db.models.signals import post_save

from rest_framework.authtoken.models import Token

from account.models import User

@receiver(post_save, sender=User)
def generate_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user = instance)
