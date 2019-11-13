import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from celery import Celery
from kombu import Exchange, Queue

from .. import configs
from ..snippets import logger
from .xmpp_client import BaseClassForTask


app = Celery('fanava-SMTP', broker=configs.Messaging.CELERY_BROKER,
             backend=configs.Messaging.CELERY_BACKEND)

app.conf.task_queues = (
    Queue(configs.Messaging.SMTP_QUEUE, Exchange(configs.Messaging.GENERAL_EXCHANGE),
          routing_key=configs.Messaging.SMTP_ROUTING_KEY),
)

app.conf.task_routes = {
    'fanava.messaging.general_publisher': {'queue': configs.Messaging.SMTP_QUEUE}
}


@app.task(name='fanava.messaging.general_publisher', bind=True,
          base=BaseClassForTask)
def celery_send_mail(self, data):
    logger('SMTP client called to send message', data)

    msg = MIMEMultipart()
    msg['From'] = configs.Messaging.SMTP_CLIENT_USERNAME
    msg['Subject'] = data['subject']
    msg.attach(MIMEText(data['body'], 'html'))

    # data[to] is a list of emails now
    msg['To'] = ', '.join(data['to'])
    if data['cc']:
        msg['Cc'] = ', '.join(data['cc'][0])

    # in case of use of SMTP_SSL connection with fanava server IP causes error
    # so I had to use SMTP but enable TLS

    server = smtplib.SMTP(configs.Messaging.SMTP_SERVER_ADDRESS,
                          configs.Messaging.SMTP_SERVER_PORT)

    server.ehlo()
    server.starttls()  # enable TLS
    server.ehlo()

    # login to mail
    server.login(configs.Messaging.SMTP_CLIENT_USERNAME,
                 configs.Messaging.SMTP_CLIENT_PASSWORD)

    # send message
    server.send_message(msg)

    server.close()

    logger('SMTP email sent successfully', data)
