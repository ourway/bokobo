import logging
import random
from uuid import uuid4

from helper import Http_error, value
from log import LogMsg
from app_redis import app_redis as redis
from send_message.send_message import send_message
from repository.user_repo import check_by_cell_no
from messages import Message


def app_ping():
    return {"result":"app is on"}


def activate_account(data,db_session):
    valid_activating_intervall = value('valid_registering_intervall',86400)

    logging.info(LogMsg.START + ' data is: '+str(data))

    cell_no = data.get('cell_no')
    if cell_no is None:
        logging.error(LogMsg.DATA_MISSING.format('cell_no'))
        raise Http_error(404,Message.MSG6)

    logging.debug(LogMsg.CHECK_USER_EXISTANCE)

    if check_by_cell_no(cell_no,db_session):
        logging.error(LogMsg.USER_XISTS)
        raise Http_error(409,Message.MSG1)

    logging.debug(LogMsg.CHECK_REDIS_FOR_EXISTANCE)

    activation_code = redis.get(cell_no)
    if activation_code is None:
        logging.error(LogMsg.REGISTER_KEY_DOESNT_EXIST)
        raise Http_error(404,Message.MSG2)

    activation_code = activation_code.decode("utf-8")
    if activation_code != data.get('activation_code'):
        logging.error(LogMsg.REGISTER_KEY_INVALID)
        raise Http_error(409, Message.MSG3)

    signup_token = str(uuid4())
    redis.delete(cell_no)
    redis.set(cell_no, signup_token, ex=valid_activating_intervall)

    data = {'cell_no': cell_no, 'signup_token':signup_token}

    return data

def register(data,db_session):
    valid_registering_intervall = value('valid_registering_intervall', 60)

    logging.info(LogMsg.START + ' data is: ' + str(data))

    cell_no = data.get('cell_no')
    if cell_no is None:
        logging.error(LogMsg.DATA_MISSING.format('cell_no'))
        raise Http_error(404, Message.MSG6)

    logging.debug(LogMsg.CHECK_USER_EXISTANCE)

    if check_by_cell_no(cell_no, db_session):
        logging.error(LogMsg.USER_XISTS)
        raise Http_error(409, Message.MSG1)

    logging.debug(LogMsg.CHECK_REDIS_FOR_EXISTANCE)

    if redis.get(cell_no):
        logging.error(LogMsg.REGISTER_XISTS)
        raise Http_error(403, {'msg':Message.MSG4,'time':redis.ttl(cell_no)})

    logging.debug(LogMsg.GENERATING_REGISTERY_CODE.format(cell_no))

    password = random.randint(1000, 9999)


    message = '  کتابخوان جام جم \n کد احراز هویت شما : {}'.format(password)
    data = {'receptor': cell_no, 'message': message,'sender':value('sms_sender',None)}

    logging.debug(LogMsg.SEND_CODE_BY_SMS.format(cell_no))
    sent_data = send_message(data)
    if sent_data.get('status') != 200:
        raise Http_error(501,Message.MSG5)

    redis.set(cell_no, password, ex=valid_registering_intervall)
    result = {'msg':Message.MSG7,'cell_no':cell_no,'time':redis.ttl(cell_no)}
    logging.debug(LogMsg.SMS_SENT.format(cell_no))

    return result