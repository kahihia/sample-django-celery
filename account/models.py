from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _

import uuid
from datetime import datetime, timedelta, timezone
import random


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('User must have an email address.')
        if not username:
            raise ValueError('User must have a username.')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=email.split('@')[0],
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.is_email_verified = True
        user.save(using=self._db)
        return user


def get_user_display_pic(user, filename):
    return f'display_pics/{user.id}/display_pic.png'


def get_default_display_pic():
    return 'default/dummy_image.png'


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        verbose_name = _('ID'),
        primary_key = True,
        default = uuid.uuid4,
        editable = False,
    )
    email = models.EmailField(
        verbose_name = _('Email'),
        max_length = 64,
        unique = True,
        error_messages = {
            'null' : _('Email field is required.'),
            'unique' : _('AN account with that email already exists. Please login to continue.'),
            'invalid' : _('Enter a valid email address.'),
        }
    )
    username = models.CharField(
        verbose_name = _('Username'),
        max_length = 64,
        unique = True,
        error_messages = {
            'null' : _('Username field is required.'),
            'unique' : _('An account with that username already exists.'),
            'invalid' : _('Enter a valid email address.'),
        }
    )
    name = models.CharField(
        verbose_name = _('Full Name'),
        max_length = 64,
        null = True,
        blank = True
    )
    is_staff = models.BooleanField(
        verbose_name = _('Staff Status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        verbose_name = _('Active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active.'
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_email_verified = models.BooleanField(
        verbose_name = _('Email Verification Status'),
        default=False,
        help_text=_(
            'Designates whether this user is verified or not.'
        ),
    )
    hide_email = models.BooleanField(
        verbose_name = _('Hide Email'),
        default=False,
        help_text=_(
            'Designates whether this user wants to show or hide their email ID.'
        ),
    )
    last_login = models.DateTimeField(
        verbose_name = _('Last Login'),
        auto_now = True,
    )
    date_joined = models.DateTimeField(
        verbose_name = _('Date Joined'),
        auto_now_add = True,
        editable = False,
    )
    display_pic = models.ImageField(
        verbose_name = _('Profile Picture'),
        null = True,
        blank = True,
        default = get_default_display_pic,
        upload_to = get_user_display_pic,
    )
    text = models.TextField(
        verbose_name=_('Text'),
        max_length=32,
        null=True,
        blank=True
    )

    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.username

    def get_display_pic_name(self):
        return str(self.display_pic)[str(self.display_pic).index(f'display_pics/{self.id}/'):]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']


def getExpiryTime():
    return datetime.now() + timedelta(minutes=5)

def getOTPToken():
    return random.randrange(100000, 999999)

class OTPToken(models.Model):
    id = models.UUIDField(
        verbose_name = _('ID'),
        primary_key = True,
        default = uuid.uuid4,
        editable = False,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    token = models.IntegerField(
        verbose_name = _('Token'),
        default=getOTPToken,
        editable=False
    )
    expiry_time = models.DateTimeField(
        verbose_name = _('Expiry Time'),
        default=getExpiryTime,
        editable=False
    )

    def __str__(self):
        return self.user.name + str(self.token)

    @property
    def is_expired(self):
        return self.expiry_time < datetime.now(timezone.utc)

