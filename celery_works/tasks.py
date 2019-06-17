from __future__ import absolute_import, unicode_literals

from .celery import app


@app.task
def test():
    return 'nasim is here'


@app.task(name='jjp.sms',bind=True)
def xsum(numbers):
    return sum(numbers)
