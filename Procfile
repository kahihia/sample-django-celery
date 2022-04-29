web: gunicorn basic.wsgi --log-file -
worker_and_beat: REMAP_SIGTERM=SIGQUIT celery -A basic.celery worker --loglevel=info -B