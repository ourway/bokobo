import json
import logging
import random
from uuid import uuid4

from helper import Http_error, value
from log import LogMsg
from app_redis import app_redis as redis
from send_message.send_message import send_message
from repository.user_repo import check_by_cell_no, check_by_username
from messages import Message
from user.controllers.person import get as get_person


def app_ping():
    return {"result":"app is on"}


def activate_account(data,db_session):
    valid_activating_intervall = value('valid_activating_intervall',86400)

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

    cell_data = redis.get(cell_no)
    if cell_data is None:
        logging.error(LogMsg.REGISTER_KEY_DOESNT_EXIST)
        raise Http_error(404,Message.MSG2)

    activation_code = (json.loads(cell_data.decode("utf-8"))).get('activation_code',None)
    print(activation_code)
    if activation_code is None:
        logging.error(LogMsg.USER_HAS_SIGNUP_TOKEN)
        raise Http_error(404, Message.MSG2)

    if activation_code != data.get('activation_code'):
        logging.error(LogMsg.REGISTER_KEY_INVALID)
        raise Http_error(409, Message.MSG3)

    signup_token = str(uuid4())
    redis.delete(cell_no)
    redis.set(cell_no, json.dumps({'signup_token':signup_token}), ex=valid_activating_intervall)

    data = {'cell_no': cell_no, 'signup_token':signup_token}

    return data


def register(data,db_session):
    valid_registering_intervall = value('valid_registering_intervall', 200)

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

    cell_data = redis.get(cell_no)

    if cell_data:
        logging.error(LogMsg.REGISTER_XISTS)
        activation_code = (json.loads(cell_data.decode('utf-8'))).get('activation_code',None)
        if activation_code:
            logging.error(LogMsg.USER_HAS_ACTIVATION_CODE)
            raise Http_error(403, {'msg':Message.MSG4,'time':redis.ttl(cell_no)})
        else:
            logging.error((LogMsg.USER_HAS_SIGNUP_TOKEN))
            redis.delete(cell_no)
    logging.debug(LogMsg.GENERATING_REGISTERY_CODE.format(cell_no))

    password = str(random.randint(1000, 9999))


    message = '  کتابخوان جام جم \n کد احراز هویت شما : {}'.format(password)
    data = {'receptor': cell_no, 'message': message,'sender':value('sms_sender',None)}

    logging.debug(LogMsg.SEND_CODE_BY_SMS.format(cell_no))
    sent_data = send_message(data)
    if sent_data.get('status') != 200:
        raise Http_error(501,Message.MSG5)

    redis.set(cell_no, json.dumps({'activation_code':password}), ex=valid_registering_intervall)
    result = {'msg':Message.MSG7,'cell_no':cell_no,'time':redis.ttl(cell_no)}
    logging.debug(LogMsg.SMS_SENT.format(cell_no))

    return result


def forget_pass(data, db_session):
    reset_password_interval = value('reset_password_interval',120)
    username = data.get('username')
    cell_no = data.get('cell_no')

    user = None
    if username:
        user = check_by_username(username, db_session)
    elif cell_no:
        user = check_by_cell_no(cell_no, db_session)
    else:
        raise Http_error(400, Message.USERNAME_CELLNO_REQUIRED)

    if user:
        person = get_person(user.person_id, db_session, username)
        password = str(random.randint(1000, 9999))
        message = 'کد زیر وارد را کرده و سپس کلمه عبور خود را تغییر دهید:  {}'.format(password)
        sending_data = {'receptor': person.cell_no, 'message': message}
        send_message(sending_data)
        redis_key = 'PASS_{}'.format(person.cell_no)
        redis.set(redis_key,password,ex=reset_password_interval)
        return {'msg': 'successful'}

    raise Http_error(404, Message.INVALID_USER)
