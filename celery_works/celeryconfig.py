from kombu import Queue, Exchange

broker_url = 'pyamqp://guest@localhost//'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Oslo'
enable_utc = True

# task_default_queue = 'default'

#
task_routes = {
    'sms': {'queue': 'sms'},
    'book_generate':{'queue':'book_generate'}
}
#
# # task_routes = {
# #     'celery.generate_book_content': 'book_generate',
# # }
#
task_queues = {
    Queue('sms',Exchange('sms'),routing_key='sms'),
    Queue('book_generate', Exchange('book_generate'), routing_key='book_generate')

}
#
#
# #
# # task_annotations = {
# #     'tasks.add': {'rate_limit': '10/m'}
# # }
#
#
