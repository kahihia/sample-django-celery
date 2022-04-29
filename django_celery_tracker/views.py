import json
from datetime import timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.response import HttpResponse, SimpleTemplateResponse
from django.utils.dateparse import parse_datetime
from django.views.generic import FormView
from celery.result import AsyncResult

from django_celery_tracker.decorators import admin_required
from django_celery_tracker.helpers import (
    get_task_created_item,
    get_task_data,
)
from django_celery_tracker.models import CeleryTask

from .forms import TextFormModelForm
from .tasks import text_task

from django.shortcuts import render

class TextFormView(FormView):
    form_class = TextFormModelForm
    template_name = "celery_tracker/timeline_dashboard.html"
    success_url = "/"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['celery_track'] = CeleryTask.objects.all()
        return ctx
    def form_valid(self, form):
        form.save()
        self.process_text(form.cleaned_data)

        return super().form_valid(form)

    def process_text(self, valid_data):
        text = valid_data["text"]

        text_task.delay(
            text
        )




@admin_required
def task_details(request, task_id):
    task = get_object_or_404(CeleryTask, task_id=task_id)
    res = AsyncResult(task_id)

    details = {
        'task_name': task.task_name,
        'task_id': task_id,
        'args': task.args,
        'created': task.created,
        'started': task.started,
        'completed': task.completed,
    }

    try:
        details['state'] = res.state
        if res.traceback is not None:
            details['traceback'] = str(res.traceback).replace('\n', '<br/>')
    except TypeError:
        # Celery doesn't have a record of this uuid
        details['state'] = 'UNKNOWN'

    if task.post_state:
        details['state'] = task.post_state

    return HttpResponse(
        json.dumps(details, cls=DjangoJSONEncoder),
        content_type='application/json',
    )
