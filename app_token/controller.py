import json
from uuid import uuid4
import logging
from log import Msg
from helper import Now, Http_error, value
from send_message import send_message
from .models import APP_Token

token_expiration_interval = value('token_expiration_interval', '120')
new_token_request_valid_interval = value('new_token_request_valid_interval','30')


def add(db_session, data, username):
    logging.info(Msg.START)

    current_token = get_current_token(db_session, username)

    if current_token is not None and \
            current_token.expiration_date > Now() + int(new_token_request_valid_interval):
        return current_token

    model_instance = APP_Token()
    model_instance.id = str(uuid4())
    model_instance.username = username
    model_instance.expiration_date = Now() + int(token_expiration_interval)

    logging.debug(Msg.DATA_ADDITION + "  || Data :" + json.dumps(data))

    db_session.add(model_instance)

    logging.debug(Msg.TOKEN_CREATED)

    logging.info(Msg.END)

    return model_instance


def get(id, db_session, username):
    logging.info(Msg.START + "user is {}".format(username))

    model_instance = db_session.query(APP_Token) \
        .filter(APP_Token.id == id).first()
    if model_instance:
        logging.info(Msg.MODEL_GETTING)
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, Msg.NOT_FOUND)

    logging.debug(Msg.GET_SUCCESS)

    if model_instance.expiration_date < Now():
        logging.error(Msg.TOKEN_EXPIRED)
        raise Http_error(401,'not valid token')

    logging.info(Msg.END)
    return model_instance


def delete(id, db_session, username):
    logging.info(Msg.START + "user is {}  ".format(username) + "token_id = {}".format(id))

    logging.info(Msg.DELETE_REQUEST + "user is {}".format(username))

    try:
        db_session.query(APP_Token).filter(APP_Token.id == id).delete()

        logging.debug(Msg.TOKEN_DELETED + "APP_Token.id {}".format(id))

    except:
        logging.error(Msg.DELETE_FAILED)
        raise Http_error(500, Msg.DELETE_FAILED)

    logging.info(Msg.END)
    return {}


def get_all(db_session, username):
    logging.info(Msg.START + "user is {}".format(username))
    try:
        result = db_session.query(APP_Token).all()
        logging.debug(Msg.GET_SUCCESS)
    except:
        logging.error(Msg.GET_FAILED)
        raise Http_error(500, Msg.GET_FAILED)

    logging.debug(Msg.END)
    return result


def get_current_token(db_session, username):
    token = db_session.query(APP_Token). \
        filter(APP_Token.username == username,
               APP_Token.expiration_date > Now()).first()
    return token

