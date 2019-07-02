import json
import logging
import os
from uuid import uuid4

from helper import model_to_dict, Now, value, Http_error
from  log import logger,LogMsg
from ..models import Person, User
from repository.person_repo import person_cell_exists,person_mail_exists

save_path = os.environ.get('save_path')


def add(db_session,data,username):

    if person_cell_exists(db_session,data.get('cell_no')):
        raise Http_error(409,LogMsg.PERSON_EXISTS.format('cell_no'))

    email = data.get('email')

    if email and person_mail_exists(db_session,email):
        raise Http_error(409,LogMsg.PERSON_EXISTS.format('email'))



    # logger.info(LogMsg.START,extra={'data':data,'user':username})

    model_instance = Person()
    model_instance.id = str(uuid4())
    model_instance.name = data.get('name')
    model_instance.last_name = data.get('last_name')
    model_instance.address = data.get('address')
    model_instance.phone = data.get('phone')
    model_instance.email = data.get('email')
    model_instance.cell_no = data.get('cell_no')
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1

    images = data.get('image')or[]
    image = images[0] if len(images) > 0 else None

    if image:
        image.filename = str(uuid4())
        model_instance.image = image.filename

        image.save(save_path)
        del (data['image'])



    # logger.debug(LogMsg.DATA_ADDITION)

    db_session.add(model_instance)

    # logger.debug(LogMsg.DB_ADD,extra = {'person':model_to_dict(model_instance)})

    # logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username):
    #TODO: for string manipulation use format and dont use '+' for string concatation "{} user is {} getting user_id={}".format(LogMsg.START, username, id)
    logging.info(LogMsg.START
                 + "user is {}  ".format(username)
                 + "getting user_id = {}".format(id))
    logging.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance:

        logging.debug(LogMsg.GET_SUCCESS +
                      json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": LogMsg.NOT_FOUND})
    #TODO: as mentioned before, "{} id:{}".format(LogMsg.GET_FAILED, id)
    logging.error(LogMsg.GET_FAILED + json.dumps({"id": id}))
    logging.info(LogMsg.END)

    return model_instance

def edit(db_session,data,username):
    #TODO: you never checked version of passed data, we have version field in our
    #      records, to prevent conflict when we received two different edit request
    #      concurrently. check KAVEH codes (edit functions) to better understanding
    #      version field usage
    logging.info(LogMsg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
        logging.debug(LogMsg.EDIT_REQUST)

    model_instance = get(id, db_session,username)
    if model_instance:
        logging.debug(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": LogMsg.NOT_FOUND})

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

    logging.debug(LogMsg.MODEL_ALTERED)

    logging.debug(LogMsg.EDIT_SUCCESS +
                  json.dumps(model_to_dict(model_instance)))

    logging.info(LogMsg.END)

    return model_instance


def delete(id, db_session, username):
    logging.info(LogMsg.START + "user is {}  ".format(username) + "token_id = {}".format(id))

    logging.info(LogMsg.DELETE_REQUEST + "user is {}".format(username))

    try:
        db_session.query(Person).filter(Person.id == id).delete()

        logging.debug(LogMsg.ENTITY_DELETED + "Person.id {}".format(id))

        user = db_session.query(User).filter(User.person_id == id).first()

        if user:
            logging.debug(LogMsg.RELATED_USER_DELETE.format(user.id))

            db_session.query(User).filter(User.person_id == id).delete()
            logging.debug(LogMsg.ENTITY_DELETED + "USER By id = {}".format(user.id))

    except:
        logging.error(LogMsg.DELETE_FAILED)
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logging.info(LogMsg.END)
    return {}


def get_all(db_session, username):
    logging.info(LogMsg.START + "user is {}".format(username))
    try:
        result = db_session.query(Person).all()
        logging.debug(LogMsg.GET_SUCCESS)
    except:
        logging.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logging.debug(LogMsg.END)
    return result