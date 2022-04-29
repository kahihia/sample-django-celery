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
