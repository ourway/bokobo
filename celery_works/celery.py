from time import sleep

from celery import Celery

from configs import CELERY_DATABASE_URI

app = Celery('jjp', backend=CELERY_DATABASE_URI, broker='pyamqp://guest@localhost//')

app.config_from_object('celery_works.celeryconfig')

task_routes = {
    'jjp.sms': {'queue': 'sms'},
    'book_generate':{'queue':'book_generate'}
}

@app.task(name='book_generate')
def generate_book_content(data,**kwargs):
    return data


@app.task(name='jjp.sms',bind=True)
def xsum(numbers):
    return sum(numbers)