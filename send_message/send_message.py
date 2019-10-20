from kavenegar import *


from helper import value, Http_error
from log import logger, LogMsg
from messages import Message

sms_api_key = value('sms_api_key',None)
sms_timeout = value('sms_timeout',20)

def send_message(data):

    receptor = data.get('receptor')
    if receptor.startswith('0999'):
        data['receptor'] = '09357364928'
    if sms_api_key is None:
        logger.error(LogMsg.DATA_MISSING,{'sms_api_key':sms_api_key})
        raise Http_error(400,Message.MISSING_REQUIERED_FIELD)
    try:
        api = KavenegarAPI(sms_api_key)
        params = data
        response = api.verify_lookup(params)
        print(response)
        logger.debug(LogMsg.MESSAGE_SENT,response)
    except APIException as e:
        logger.exception(LogMsg.MESSAGE_NOT_SENT,exc_info=True)
        print(e)
        return {'status': 500}
    except HTTPException as e:
        logger.exception(LogMsg.MESSAGE_NOT_SENT,exc_info=True)
        print(e)
        return {'status': 500}

    return {'status':200}


