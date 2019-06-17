from celery import Celery

from configs import CELERY_DATABASE_URI

app = Celery('celery_works', backend=CELERY_DATABASE_URI, broker='pyamqp://guest@localhost//',
             include=['celery_works.tasks'])

app.config_from_object('celery_works.celeryconfig')


