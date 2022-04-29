 # [Sample Django With Celery](https://github.com/app-generator/sample-django-celery)

> Features:

-  Landing page display all tasks (active and finished + input provided by the user)
- Users can submit tasks using a String Input
- Tasks will start using the input, log the string, and exit
- SQLite persistence where all tasks are saved (id, execution status, input)
- Styling: Bootstrap 5
- Landing page elements will use BS5 default components

<br />

## âœ¨ How to use it


1. Download Redis

   redis server 
   
   ***Linux*** [https://redis.io/download]
                            
   ***Windows*** [https://github.com/tporadowski/redis/releases]

2. Open & Test Redis:

    open Terminal

    redis-cli ping

    $ redis-cli ping
    PONG

    Close Redis with control + c to quit
	
Locally After All:
[
Start Redis server
Start celery: celery -A basic.celery worker -l info
Start simple beat: celery -A basic.celery  beat -l info
Start database beat: celery -A basic.celery  beat -S django
]

3. Install Celery + Redis in your virtualenv.

pip install celery

pip install redis

pip install django-celery-beat

pip install django-celery-results

pip freeze > requirements.txt

4. Update Django settings.py:

INSTALLED_APPS = [
    
	'django.contrib.admin',
	
    'django.contrib.auth',
	
    'django.contrib.contenttypes',
	
    'django.contrib.sessions',
	
    'django.contrib.messages',
	
    'django.contrib.staticfiles',
	
    'rest_framework',
	
    'rest_framework.authtoken',
	
    'corsheaders',
	
    'django_celery_results',
	
    'django_celery_beat',
	
    'account',   # Custom user account and profile app
	
	'django_celery_tracker',  # Our main app for the task creation
]


#Update CELERY_SETTINGS

CELERY_BROKER_URL = 'redis://localhost:6379'

CELERY_RESULT_BACKEND = 'redis://localhost:6379'

CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_TASK_SERIALIZER = 'json'

CELERY_RESULT_SERIALIZER = 'json'

CELERY_TIMEZONE = TIME_ZONE

5. Create celery.py to setup Celery app: Navigate to project config module (where settings and urls modules are) and create a celery.py file with the contents:

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

6. Create tasks.py in your Django main app ("django_celery_tracker") :

from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True)
def text_task(self, text):
    try:
        logger.info("About to print text")
        print(text)
    except BadHeaderError:
        logger.info("BadHeaderError")
    except Exception as e:
        logger.error(e)

7. Create views.py to invoke task when text is submited from form.

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

We use .delay() to tell Celery to add the task to the queue.

We got back a successful AsyncResult — that task is now waiting in Redis for a worker to pick it up!
text_task.delay() (should see `<AsyncResult: c6ef74b9-4c03-402a-b1db-9e2adbf52f75>`)

8. Create django_celery_tracker/signals.py.  We use celery signals to log tasks status and activities. 

from celery.signals import before_task_publish, task_prerun, task_postrun


@before_task_publish.connect
def task_publish_handler(sender=None, headers=None, body=None, **kwargs):
    from django_celery_tracker.models import CeleryTask
    info = headers if 'task' in headers else body
    print(info)
    CeleryTask.objects.get_or_create(
        task_id=info['id'], task_name=info['task'], args=info['argsrepr']
    )


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, **kwargs):
    from django_celery_tracker.models import CeleryTask
    from django.utils import timezone

    t = CeleryTask.objects.get_or_create(task_id=task_id)[0]
    t.started = timezone.now()
    t.save(update_fields=['started'])


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, state=None, **kwargs):
    from django_celery_tracker.models import CeleryTask
    from django.utils import timezone

    t = CeleryTask.objects.get_or_create(task_id=task_id)[0]
    t.completed = timezone.now()
    if state is not None:
        t.post_state = state
    else:
        t.post_state = 'PREMATURE_SHUTDOWN'
    t.save(update_fields=['completed', 'post_state'])

9. In models.py, give the following

		
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


10. Run migrations: python manage.py makemigrations and python manage.py migrate
		

###################### DEPLOY ON HEROKU #####################
1) .gitignore (get rid of local environ but create requirements.txt instead)
2) same level as manage.py CREATE Procfile:
In Procfile:
web: gunicorn basic.wsgi --log-file -
worker_and_beat: REMAP_SIGTERM=SIGQUIT celery -A basic.celery worker --loglevel=info -B

3) pip install django psycopg2 dj-database-url gunicorn
4) git init
5) git add .
6) git commit -m "First Init"
7) heroku create
8.1) heroku addons:create heroku-postgresql:hobby-dev
8.2) install redis ~ heroku addons:create heroku-redis:hobby-dev
9) in settings.py under database: (will override the settings to use postgresql database if "DATABASE_URL" database environment available.) 
if 'DATABASE_URL' in os.environ:

    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }

else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

10) git add .
11) git commit -m "change database"

12) heroku config:set DISABLE_COLLECTSTATIC=1

13.1) git push heroku master
13.2) After pushing: SCALE:
~ heroku ps:scale web=1 worker=1
OR if using schedule
~ heroku ps:scale web=1 worker=1 beat=1 (must be paid plan)

14) heroku run python manage.py migrate
15) heroku run bash
16) python manage.py createsuperuser
17) heroku open


heroku restart

