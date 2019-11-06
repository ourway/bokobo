import requests
from kavenegar import *

from helper import value, Http_error
from log import logger, LogMsg
from messages import Message

sms_token_url = value('sms_token_url', 'https://RestfulSms.com/api/Token')
sms_security_key = value('sms_security_key', 'Jame_jam@nsm5msd&*!')
sms_api_key = value('sms_api_key', '51493c0cc42cd23559c73c0c')
sms_timeout = value('sms_timeout', 20)
sms_send_url = value('sms_send_url', 'https://RestfulSms.com/api/MessageSend')
sms_line_no = value('sms_line_no','10005195')


def send_message(data):
    receptor = data.get('receptor')
    if receptor.startswith('0999'):
        data['receptor'] = '09357364928'
    if sms_api_key is None:
        logger.error(LogMsg.DATA_MISSING, {'sms_api_key': sms_api_key})
        raise Http_error(400, Message.MISSING_REQUIERED_FIELD)
    try:
        api = KavenegarAPI(sms_api_key)
        params = data
        response = api.verify_lookup(params)
        print(response)
        logger.debug(LogMsg.MESSAGE_SENT, response)
    except APIException as e:
        logger.exception(LogMsg.MESSAGE_NOT_SENT, exc_info=True)
        print(e)
        return {'status': 500}
    except HTTPException as e:
        logger.exception(LogMsg.MESSAGE_NOT_SENT, exc_info=True)
        print(e)
        return {'status': 500}

    # token_data = {
    #     'UserApiKey': sms_api_key,
    #     'SecretKey': sms_security_key
    # }
    #
    # token_response = requests.post(sms_token_url, data=token_data)
    # res = token_response.json()
    # if not res.get('IsSuccessful'):
    #     logger.error(LogMsg.MESSAGE_NOT_SENT, res)
    #     raise Http_error(500, Message.MESSAGE_NOT_SENT)
    #
    # token = res['TokenKey']
    #
    # headers = {'Content-Type': 'application/json',
    #            'x-sms-ir-secure-token': token}
    # message_data = {
    #     'Messages': [data.get('message', 'SALAAM')],
    #     'MobileNumbers': ['09143091780', '09360076133', '09357364928'],
    #     'LineNumber': sms_line_no
    # }
    #
    # sms_sent = requests.post(sms_send_url, headers=headers, json=message_data)
    # sms_data = sms_sent.json()
    # if not sms_data['IsSuccessful']:
    #     logger.error(LogMsg.MESSAGE_NOT_SENT, sms_data)
    #     raise Http_error(500, Message.MESSAGE_NOT_SENT)
    return {'status':200}

