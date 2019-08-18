import json
import logging
import os
from uuid import uuid4

from sqlalchemy import or_

from accounts.controller import add_initial_account
from follow.controller import get_following_list_internal
from helper import model_to_dict, Now, Http_error, model_basic_dict
from log import LogMsg
from messages import Message
from repository.library_repo import library_to_dict
from wish_list.controller import get_wish_list, internal_wish_list
from ..models import Person, User
from repository.person_repo import person_cell_exists, person_mail_exists
from books.controllers.book import get_current_book

save_path = os.environ.get('save_path')


def add(db_session, data, username):
    cell_no = data.get('cell_no')
    if cell_no and person_cell_exists(db_session, cell_no):
        raise Http_error(409, LogMsg.PERSON_EXISTS.format('cell_no'))

    email = data.get('email')

    if email and person_mail_exists(db_session, email):
        raise Http_error(409, LogMsg.PERSON_EXISTS.format('email'))

    # logger.info(LogMsg.START,extra={'data':data,'user':username})

    model_instance = Person()
    model_instance.id = str(uuid4())
    model_instance.name = data.get('name')
    model_instance.last_name = data.get('last_name')
    model_instance.address = data.get('address')
    model_instance.phone = data.get('phone')
    model_instance.email = data.get('email')
    model_instance.cell_no = data.get('cell_no')
    model_instance.bio = data.get('bio')
    model_instance.tags = data.get('tags')
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    model_instance.image = data.get('image')

    db_session.add(model_instance)
    add_initial_account(model_instance.id, db_session, username)

    return model_instance


def get(id, db_session, username):
    # TODO: for string manipulation use format and dont use '+' for string concatation "{} user is {} getting user_id={}".format(LogMsg.START, username, id)
    logging.info(LogMsg.START
                 + "user is {}  ".format(username)
                 + "getting user_id = {}".format(id))
    logging.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance:
        person_dict = person_to_dict(model_instance,db_session)
        logging.debug(LogMsg.GET_SUCCESS +
                      json.dumps(person_dict))
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)
    # TODO: as mentioned before, "{} id:{}".format(LogMsg.GET_FAILED, id)
    logging.error(LogMsg.GET_FAILED + json.dumps({"id": id}))
    logging.info(LogMsg.END)

    return person_dict


def edit(id, db_session, data, username):
    # TODO: you never checked version of passed data, we have version field in our
    #      records, to prevent conflict when we received two different edit request
    #      concurrently. check KAVEH codes (edit functions) to better understanding
    #      version field usage

    logging.info(LogMsg.START + " user is {}".format(username))

    if "id" in data.keys():
        del data["id"]
        logging.debug(LogMsg.EDIT_REQUST)

    model_instance = get(id, db_session, username)
    if model_instance:
        logging.debug(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": LogMsg.NOT_FOUND})

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    model_instance.modification_date = Now()
    model_instance.modifier = username
    model_instance.version += 1

    logging.debug(LogMsg.MODEL_ALTERED)

    logging.debug(LogMsg.EDIT_SUCCESS +
                  json.dumps(model_to_dict(model_instance)))

    logging.info(LogMsg.END)

    return model_instance


def delete(id, db_session, username):
    logging.info(
        LogMsg.START + "user is {}  ".format(username) + "token_id = {}".format(
            id))

    logging.info(LogMsg.DELETE_REQUEST + "user is {}".format(username))

    try:
        db_session.query(Person).filter(Person.id == id).delete()

        logging.debug(LogMsg.ENTITY_DELETED + "Person.id {}".format(id))

        user = db_session.query(User).filter(User.person_id == id).first()

        if user:
            logging.debug(LogMsg.RELATED_USER_DELETE.format(user.id))

            db_session.query(User).filter(User.person_id == id).delete()
            logging.debug(
                LogMsg.ENTITY_DELETED + "USER By id = {}".format(user.id))

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


def search_person(data, db_session,username):
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)
    filter = data.get('filter', None)

    result = []

    try:
        if filter is None:
            persons = db_session.query(Person).order_by(
                Person.creation_date.desc()).slice(offset,
                                                   offset + limit)

        else:
            person_name = filter.get('person')
            if person_name is None:
                raise Http_error(400,Message.MISSING_REQUIERED_FIELD)


            persons = db_session.query(Person).filter(
                or_(Person.name.like('%{}%'.format(person_name)),
                    Person.last_name.like('%{}%'.format(person_name)))
            ).order_by(
                Person.creation_date.desc()).slice(offset,
                                                   offset + limit)

        for person in persons:
            result.append(model_to_dict(person))
    except:
        raise Http_error(404, Message.MSG20)

    return result


def get_person_profile(id, db_session, username):
    # TODO: for string manipulation use format and dont use '+' for string concatation "{} user is {} getting user_id={}".format(LogMsg.START, username, id)
    logging.info(LogMsg.START
                 + "user is {}  ".format(username)
                 + "getting user_id = {}".format(id))
    logging.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance:
        result = model_to_dict(model_instance)
        result['current_book'] = get_current_book(
            model_instance.current_book_id, db_session) or None
        result['following_list'] = get_following_list_internal(id, db_session)
        result['wish_list'] = internal_wish_list(db_session, Person.id)

        logging.debug(LogMsg.GET_SUCCESS +
                      json.dumps(result))
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)
    # TODO: as mentioned before, "{} id:{}".format(LogMsg.GET_FAILED, id)
    logging.error(LogMsg.GET_FAILED + json.dumps(result))
    logging.info(LogMsg.END)

    return result


def person_to_dict(person,db_session):
    result  = model_basic_dict(person)
    model_attrs = {
        'address':person.address,
        'bio':person.bio,
        'cell_no':person.cell_no,
        'current_book_id':person.current_book_id,
        'email':person.email,
        'image':person.image,
        'name':person.name,
        'last_name':person.last_name,
        'phone':person.phone
        # 'library':library_to_dict(person.library,db_session)

    }
    result.update(model_attrs)
    return result