from time import sleep

from celery import Celery

from configs import CELERY_DATABASE_URI
from helper import Http_error
from messages import Message

app = Celery('jjp', backend=CELERY_DATABASE_URI, broker='pyamqp://guest@localhost//')

app.config_from_object('celery_works.celeryconfig')

task_routes = {
    'sms': {'queue': 'sms'},
    'book_generate':{'queue':'book_generate'}
}

@app.task(name='book_generate',bind=True)
def generate_book_content(data,**kwargs):

    sleep(60)
    # if True:
    #     raise Http_error(400,Message.INVALID_ENUM)
    return data


@app.task(name='sms',bind=True)
def xsum(numbers):
    return sum(numbers)