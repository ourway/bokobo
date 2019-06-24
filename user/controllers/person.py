import json
import logging
import os
from uuid import uuid4

from helper import model_to_dict, Now, value, Http_error
from  log import logger,Msg
from ..models import Person, User
from repository.person_repo import person_cell_exists,person_mail_exists

save_path = os.environ.get('save_path')


def add(db_session,data,username):

    if person_cell_exists(db_session,data.get('cell_no')):
        raise Http_error(409,Msg.PERSON_EXISTS.format('cell_no'))

    if person_mail_exists(db_session,data.get('email')):
        raise Http_error(409,Msg.PERSON_EXISTS.format('email'))

    # logger.info(Msg.START,extra={'data':data,'user':username})

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

    images = data.get('image',[])
    image = None
    if len(images)> 0:
        image = images[0]

    if image:
        image.filename = str(uuid4())
        model_instance.image = image.filename

        image.save(save_path)
        del (data['image'])



    # logger.debug(Msg.DATA_ADDITION)

    db_session.add(model_instance)

    # logger.debug(Msg.DB_ADD,extra = {'person':model_to_dict(model_instance)})

    # logger.info(Msg.END)
    return model_instance


def get(id, db_session, username):
    logging.info(Msg.START
                 + "user is {}  ".format(username)
                 + "getting user_id = {}".format(id))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance:

        logging.debug(Msg.GET_SUCCESS +
                      json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": Msg.NOT_FOUND})

    logging.error(Msg.GET_FAILED + json.dumps({"id": id}))

    logging.info(Msg.END)

    return model_instance

def edit(db_session,data,username):
    logging.info(Msg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
        logging.debug(Msg.EDIT_REQUST)

    model_instance = get(id, db_session,username)
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

    logging.debug(Msg.EDIT_SUCCESS +
                  json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)

    return model_instance


def delete(id, db_session, username):
    logging.info(Msg.START + "user is {}  ".format(username) + "token_id = {}".format(id))

    logging.info(Msg.DELETE_REQUEST + "user is {}".format(username))

    try:
        db_session.query(Person).filter(Person.id == id).delete()

        logging.debug(Msg.ENTITY_DELETED + "Person.id {}".format(id))

        user = db_session.query(User).filter(User.person_id == id).first()

        if user:
            logging.debug(Msg.RELATED_USER_DELETE.format(user.id))

            db_session.query(User).filter(User.person_id == id).delete()
            logging.debug(Msg.ENTITY_DELETED + "USER By id = {}".format(user.id))

    except:
        logging.error(Msg.DELETE_FAILED)
        raise Http_error(500, Msg.DELETE_FAILED)

    logging.info(Msg.END)
    return {}


def get_all(db_session, username):
    logging.info(Msg.START + "user is {}".format(username))
    try:
        result = db_session.query(Person).all()
        logging.debug(Msg.GET_SUCCESS)
    except:
        logging.error(Msg.GET_FAILED)
        raise Http_error(500, Msg.GET_FAILED)

    logging.debug(Msg.END)
    return result
