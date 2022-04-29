from django.contrib import admin

from .models import CeleryTask, TextForm

admin.site.register(TextForm)
admin.site.register(CeleryTask)
