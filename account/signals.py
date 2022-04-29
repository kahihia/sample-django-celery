import os
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete, post_save

from django.conf import settings

from account.models import User

@receiver(pre_delete, sender=User)
def account_delete(sender, instance, **kwargs):
    """
    Deleting the specific image of a Post after delete it
    """
    if instance.display_pic and instance.display_pic != 'default/dummy_image.png':
        if os.path.isfile(instance.display_pic.path):
            os.remove(instance.display_pic.path)
            os.rmdir(settings.BASE_DIR / f'media/display_pics/{instance.id}')


@receiver(pre_save, sender=User)
def account_update(sender, instance, **kwargs):
    """
    Replacing the specific image of a Post after update
    """

    try:
        old_image = sender.objects.get(id=instance.id).display_pic
        new_image = instance.display_pic
        if not (old_image == new_image or old_image == 'default/dummy_image.png'):
            if os.path.isfile(old_image.path):
                os.remove(old_image.path)
    except Exception:
        return


from rest_framework.authtoken.models import Token

@receiver(post_save, sender=User)
def generate_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user = instance)
