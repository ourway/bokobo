from kombu import Queue, Exchange

broker_url = 'pyamqp://'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Oslo'
enable_utc = True

task_default_queue = 'default'


task_routes = {
    'jjp.sms': {'queue': 'sms'}
}

task_queues = {
    Queue('sms',Exchange('sms'),routing_key='sms')
}


#
# task_annotations = {
#     'tasks.add': {'rate_limit': '10/m'}
# }


