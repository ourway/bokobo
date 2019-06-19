import inspect
import json
import logging
from uuid import uuid4

from log import Msg
from helper import Now, model_to_dict, Http_error, multi_model_to_dict
from repository.person_repo import validate_person
from repository.user_repo import check_by_username, check_by_cell_no
from user.models import User, Person


def add(db_session, data,add_user):
    logging.info(Msg.START)
    cell_no = data.get('cell_no')
    name = data.get('name')
    username = data.get('username')
    user = check_by_username(username,db_session)
    if user:
        logging.error(Msg.USER_XISTS.format(username))
        raise Http_error(409, {"username": Msg.USER_XISTS.format(username)})

    user_by_cell = check_by_cell_no(cell_no,db_session)
    if user_by_cell != None:
        logging.error(Msg.USERNAME_NOT_UNIQUE)
        raise Http_error(409, {"cell_no": Msg.USER_BY_CELL_EXIST})



    logging.debug(Msg.USR_ADDING)

    model_instance = User()
    model_instance.username = username
    model_instance.password = data.get('password')
    model_instance.name = name
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = add_user

    person_is_valid = None
    person_id = data.get('person_id')
    if person_id:
        person_is_valid = validate_person(person_id,db_session)
    if person_is_valid:
        model_instance.person_id = person_id


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
        raise Http_error(404, {"id": Msg.NOT_FOUND})

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


        if model_instance.person_id:
            model_instance.person
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"user": Msg.NOT_FOUND})

    logging.info(Msg.END + model_to_dict(model_instance))

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
        raise Http_error(404, {"id": Msg.NOT_FOUND})

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
