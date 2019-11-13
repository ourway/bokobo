

from configs import CELERY_DATABASE_URI
from .. import configs
from kombu import Queue, Exchange

from ..snippets import logger, load_template
from .xmpp_client import BaseClassForTask

#
# app.conf.task_routes = {
#     'Jam_e_Jam.consumer': {'queue': configs.BookGenerate.BOOK_GENERATE_QUEUE},
#     'Jam_e_Jam.general_publisher': {
#         'exchange': configs.BookGenerate.BOOK_GENERATE_EXCHANGE}
# }

from celery_works import configs
from ..celery import generate_book_content

def generate_book( data):
    # result = generate_book_content.apply_async(args=[data],
    #                               routing_key=configs.BookGenerate.BOOK_GENERATE_KEY)
    a=1/0
    result = generate_book_content.delay(data)
    print(result.task_id)
    # result.get()
    return result.task_id

def check_status(id):

    pass
