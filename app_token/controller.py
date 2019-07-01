import json
from uuid import uuid4
import logging
from log import LogMsg
from helper import Now, Http_error, value
from messages import Message
from send_message import send_message
from .models import APP_Token

token_expiration_interval = value('token_expiration_interval', '120')
new_token_request_valid_interval = value('new_token_request_valid_interval','30')


def add(db_session, data, username):
    logging.info(LogMsg.START)

    current_token = get_current_token(db_session, username)

    if current_token is not None and \
            current_token.expiration_date > Now():
        return current_token

    model_instance = APP_Token()
    model_instance.id = str(uuid4())
    model_instance.username = username
    model_instance.expiration_date = Now() + int(token_expiration_interval)

    logging.debug(LogMsg.DATA_ADDITION + "  || Data :" + json.dumps(data))

    db_session.add(model_instance)

    logging.debug(LogMsg.TOKEN_CREATED)

    logging.info(LogMsg.END)

    return model_instance


def get(id, db_session, username):
    logging.info(LogMsg.START + "user is {}".format(username))

    model_instance = db_session.query(APP_Token) \
        .filter(APP_Token.id == id).first()
    if model_instance:
        logging.info(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG11)

    logging.debug(LogMsg.GET_SUCCESS)

    if model_instance.expiration_date < Now():
        logging.error(LogMsg.TOKEN_EXPIRED)
        raise Http_error(401,Message.MSG12)

    logging.info(LogMsg.END)
    return model_instance


def delete(id, db_session, username):
    logging.info(LogMsg.START + "user is {}  ".format(username) + "token_id = {}".format(id))

    logging.info(LogMsg.DELETE_REQUEST + "user is {}".format(username))

    try:
        db_session.query(APP_Token).filter(APP_Token.id == id).delete()

        logging.debug(LogMsg.TOKEN_DELETED + "APP_Token.id {}".format(id))

    except:
        logging.error(LogMsg.DELETE_FAILED)
        raise Http_error(500, Message.MSG13)

    logging.info(LogMsg.END)
    return {}


def get_all(db_session, username):
    logging.info(LogMsg.START + "user is {}".format(username))
    try:
        result = db_session.query(APP_Token).all()
        logging.debug(LogMsg.GET_SUCCESS)
    except:
        logging.error(LogMsg.GET_FAILED)
        raise Http_error(500, Message.MSG14)

    logging.debug(LogMsg.END)
    return result


def get_current_token(db_session, username):
    token = db_session.query(APP_Token). \
        filter(APP_Token.username == username,
               APP_Token.expiration_date > Now()).first()
    return token

