import logging
import random

from helper import Http_error, value
from log import Msg
from app_redis import app_redis as redis
from send_message.send_message import send_message
from repository.user_register import check_user


def app_ping():
    return {"result":"app is on"}


def register(data,db_session):
    valid_registering_intervall = value('valid_registering_intervall',200)

    logging.info(Msg.START + ' data is: '+str(data))

    cell_no = data.get('cell_no')
    if cell_no is None:
        logging.error(Msg.DATA_MISSING.format('cell_no'))
        raise Http_error(404,Msg.DATA_MISSING.format('cell_no'))

    logging.debug(Msg.CHECK_USER_EXISTANCE)

    if check_user(cell_no,db_session):
        logging.error(Msg.USER_XISTS)
        raise Http_error(409,Msg.USER_XISTS)

    logging.debug(Msg.CHECK_REDIS_FOR_EXISTANCE)

    if redis.get(cell_no):
        logging.error(Msg.REGISTER_XISTS)
        raise Http_error(403,Msg.REGISTER_XISTS)

    logging.debug(Msg.GENERATING_REGISTERY_CODE.format(cell_no))

    password = random.randint(1000, 9999)
    message = ' your activation code is : {}'.format(password)
    data = {'cell_no': cell_no, 'message':message}

    logging.debug(Msg.SEND_CODE_BY_SMS.format(cell_no))
    sent_data = send_message(data)
    logging.debug(Msg.SMS_SENT.format(cell_no))

    redis.set(cell_no,password,ex= valid_registering_intervall)

    return sent_data