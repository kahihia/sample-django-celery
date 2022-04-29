"""django_celery_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from django_celery_tracker.views import (
    TextFormView,
    task_details,
)
app_name = "celery_tracker"
urlpatterns = [
    path("", TextFormView.as_view(), name="celery_tracker"),
    re_path('^task-details/(?P<task_id>[0-9A-Za-z\-]+)/$', task_details),
]
