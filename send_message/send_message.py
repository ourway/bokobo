import logging

import gammu

from helper import value

sm = gammu.StateMachine()
sm.ReadConfig()
port = value('app_port',8080)
if port=='7000':
    sm.Init()
    logging.info('sms engine initiated')
    print('sms engine initiated')


def send_message(data):
    message = {'Text': str(data.get('message')), 'SMSC': {'Location': 1},
               'Number': str(data.get('cell_no'))}
    sm.SendSMS(message)
    return data