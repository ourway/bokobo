import json
from uuid import uuid4
from log import LogMsg,logger
from helper import Now, Http_error, value
from messages import Message
from .models import APP_Token

token_expiration_interval = value('token_expiration_interval', '1200')
new_token_request_valid_interval = value('new_token_request_valid_interval','30')


def add(db_session, data, username):
    logger.info(LogMsg.START,username)

    logger.debug(LogMsg.CHECKING_VALID_TOKEN,username)

    current_token = get_current_token(db_session, username)

    if current_token is not None and \
            current_token.expiration_date > (Now()):
        logger.debug(LogMsg.USER_HAS_VALID_TOKEN,current_token.id)
        return current_token

    model_instance = APP_Token()
    model_instance.id = str(uuid4())
    model_instance.username = username
    model_instance.expiration_date = Now() + int(token_expiration_interval)

    logger.debug(LogMsg.DATA_ADDITION,data)

    db_session.add(model_instance)

    logger.debug(LogMsg.TOKEN_CREATED)

    logger.info(LogMsg.END)

    return model_instance


def get(id, db_session, username):
    logger.info(LogMsg.START ,username)

    model_instance = db_session.query(APP_Token) \
        .filter(APP_Token.id == id).first()
    if model_instance:
        logger.info(LogMsg.MODEL_GETTING)
    else:
        logger.error(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.TOKEN_INVALID)

    logger.debug(LogMsg.GET_SUCCESS)

    if model_instance.expiration_date < Now():
        logger.error(LogMsg.TOKEN_EXPIRED)
        raise Http_error(401,Message.TOKEN_EXPIRED)

    logger.info(LogMsg.END)
    return model_instance


def delete(id, db_session, username):
    logger.info(LogMsg.START,username)

    logger.info(LogMsg.DELETE_REQUEST ,{'token_id':id})

    try:
        db_session.query(APP_Token).filter(APP_Token.id == id).delete()

        logger.debug(LogMsg.TOKEN_DELETED + "APP_Token.id {}".format(id))

    except:
        logger.error(LogMsg.DELETE_FAILED)
        raise Http_error(500, Message.DELETE_FAILED)

    logger.info(LogMsg.END)
    return {}


def get_all(db_session, username,data):
    logger.info(LogMsg.START,username)
    if data.get('sort') is None:
        data['sort'] = ['creation_date-']
    try:
        result = APP_Token.mongoquery(
            db_session.query(APP_Token)).query(
            **data).end().all()
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, Message.GET_FAILED)

    logger.debug(LogMsg.END)
    return result


def get_current_token(db_session, username):
    token = db_session.query(APP_Token). \
        filter(APP_Token.username == username,
               APP_Token.expiration_date > Now()).first()
    return token

