import celery
# from slixmpp import ClientXMPP

from .. import configs, snippets


# class XMPPClient(ClientXMPP):
#
#     def __init__(self, jid, password):
#         ClientXMPP.__init__(self, jid, password)
#
#         self.add_event_handler('session_start', self.start)
#         self.add_event_handler('message', self.received_message)
#         self.am_i_online = False
#
#     def start(self, event):
#         self.send_presence()
#         self.get_roster()
#         print('user is going to be online')
#         self.am_i_online = True
#
#     def received_message(self, received_message):
#         if received_message['type'] in ['chat', 'normal']:
#             print('*' * 10, '\t',
#                   'from: "{}", '.format(received_message["from"]),
#                   '"{}"'.format(received_message['body']))
#
#     def send_im(self, towhom, what):
#         self.send_message(towhom, what, mtype='chat')


class BaseClassForTask(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.request.retries == configs.Messaging.RETRIES_COUNT:
            snippets.logger('can not get the task done', {'task_id': task_id,
                                                          'error': str(exc)})

        self.retry(countdown=configs.Messaging.RETRY_DELAY,
                   max_retries=configs.Messaging.RETRIES_COUNT)
