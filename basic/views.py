from django.shortcuts import render
from basic.tasks import celery_test

def home(request, *args, **kwargs):
    context = {}
#     celery_test.delay()
    return render(request, 'home.html', context)

def page_not_found_view(request, *args, **kwargs):
    return render(request, '404.html', status=404)
