import json
import logging
from uuid import uuid4

from log import Msg
from helper import Now, model_to_dict, Http_error
from .models import User
from app_redis import app_redis as redis


def add(db_session, data):
    logging.info(Msg.START )
    cell_no = data.get('cell_no')
    name = data.get('name')
    user = db_session.query(User).filter(User.username == cell_no).first()
    if user:
        logging.error(Msg.USER_XISTS.format(cell_no))
        raise Http_error(409, {"cell_no": Msg.USER_XISTS.format(cell_no)})

    logging.debug(Msg.CHECK_REDIS_FOR_EXISTANCE)

    activation_code = redis.get(cell_no)
    if activation_code is None:
        logging.error(Msg.REGISTER_KEY_DOESNT_EXIST)
        raise Http_error(404,{"activation_code": Msg.REGISTER_KEY_DOESNT_EXIST})

    activation_code = activation_code.decode("utf-8")
    if activation_code != data.get('activation_code'):
        logging.error(Msg.REGISTER_KEY_INVALID)
        raise Http_error(400,{"activation_code":Msg.REGISTER_KEY_INVALID})

    user_by_name = db_session.query(User).filter(User.name == name).first()
    if user_by_name !=None:
        logging.error(Msg.NAME_NOT_UNIQUE)
        raise Http_error(409,{"name":Msg.NAME_NOT_UNIQUE})

    logging.debug(Msg.USR_ADDING)

    model_instance = User()
    model_instance.username = cell_no
    model_instance.password = data.get('password')
    model_instance.name = name
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = data.get('cell_no')

    if data.get('tags') is not None:
        tags = (data.get('tags')).split(',')
        for item in tags:
            item.strip()
        model_instance.tags = tags

    logging.debug(Msg.DATA_ADDITION)

    db_session.add(model_instance)

    logging.debug(Msg.DB_ADD + json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)
    return model_instance


def get(id, db_session, username):
    logging.info(Msg.START
                 + "user is {}  ".format(username)
                 + "getting user_id = {}".format(id))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(User).filter(User.id == id).first()
    if model_instance:
        logging.debug(Msg.GET_SUCCESS +
                      json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id":Msg.NOT_FOUND})

    logging.error(Msg.GET_FAILED + json.dumps({"id": id}))

    logging.info(Msg.END)

    return model_instance

def get_profile(username, db_session):
    logging.info(Msg.START
                 + "user is {}  ".format(username))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(User).filter(User.username == username).first()
    if model_instance:
        logging.debug(Msg.GET_SUCCESS +
                      json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"user":Msg.NOT_FOUND})

    logging.info(Msg.END)

    return model_instance

def delete(id, db_session, username):
    logging.info(Msg.START + "user is {}  ".format(username)
                 + "user_id= {}".format(id))
    try:
        logging.debug(Msg.DELETE_REQUEST +
                      "user_id= {}".format(id))

        db_session.query(User).filter(User.id == id).delete()

        logging.debug(Msg.DELETE_SUCCESS)

    except:

        logging.error(Msg.DELETE_FAILED +
                      "user_id= {}".format(id))
        raise Http_error(500, Msg.DELETE_FAILED)

    logging.info(Msg.END)

    return {}


def get_all(db_session, username):
    logging.info(Msg.START + "user is {}".format(username))
    try:
        logging.debug(Msg.GET_ALL_REQUEST + "Users...")
        result = db_session.query(User).all()

        logging.debug(Msg.GET_SUCCESS)

    except:

        logging.error(Msg.GET_FAILED)
        raise Http_error(500, Msg.GET_FAILED)

    logging.info(Msg.END)

    return result


def edit(id, db_session, data, username):
    logging.info(Msg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]

    logging.debug(Msg.EDIT_REQUST)

    model_instance = get(id, db_session, username)
    if model_instance:
        logging.debug(Msg.MODEL_GETTING)
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id":Msg.NOT_FOUND})

    if data.get('tags') is not None:
        tags = (data.get('tags')).split(',')
        for item in tags:
            item.strip()
        model_instance.tags = tags

        del data['tags']

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
        model_instance.modification_date = Now()
        model_instance.modifier = username

    logging.debug(Msg.MODEL_ALTERED)

    # db_session.add(model_instance)

    logging.debug(Msg.EDIT_SUCCESS +
                  json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)

    return model_instance

