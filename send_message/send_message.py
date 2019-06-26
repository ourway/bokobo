import logging
from kavenegar import *


from helper import value

sms_api_key = value('sms_api_key',None)

def send_message(data):
    try:
        api = KavenegarAPI(sms_api_key)
        params = {
            'sender': '1000596446',  # optinal
            'receptor': data.get('receptor'),  # multiple mobile number, split by comma
            'message': data.get('message'),
        }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
        return {'status': 500}
    except HTTPException as e:
        print(e)
        return {'status': 500}

    return {'status':200}


