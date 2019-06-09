from celery import Celery

app = Celery('tasks', backend='rpc://',broker='pyamqp://guest@localhost//')
app.config_from_object('celeryconfig')


@app.task
def test():
    return 'nasim is here'