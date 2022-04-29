from django.contrib.auth import get_user_model
from django.db import models
User = get_user_model()

class TextForm(models.Model):
    text = models.CharField(max_length=64)
    created_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "textinputform"
        verbose_name = "text form input"
        verbose_name_plural = "text input form"

    def __str__(self):
        return self.text
		
class CeleryTask(models.Model):
    task_id = models.CharField(max_length=64, db_index=True, unique=True)
    task_name = models.CharField(max_length=512)
    args = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    started = models.DateTimeField(null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)
    post_state = models.CharField(max_length=24, blank=True)
    progress = models.PositiveIntegerField(default=0)
    progress_target = models.PositiveIntegerField(default=100)

    def __str__(self):
        return "id=%s, name=%s" % (self.task_id, self.task_name)


