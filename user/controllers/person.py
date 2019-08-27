import json
import os
from uuid import uuid4

from sqlalchemy import or_

from accounts.controller import add_initial_account
from follow.controller import get_following_list_internal
from helper import model_to_dict, Now, Http_error, model_basic_dict, \
    populate_basic_data, edit_basic_data, Http_response
from log import LogMsg, logger
from messages import Message
from repository.account_repo import delete_person_accounts
from repository.book_role_repo import person_has_books
from repository.library_repo import library_to_dict
from wish_list.controller import get_wish_list, internal_wish_list
from ..models import Person, User
from repository.person_repo import person_cell_exists, person_mail_exists
from books.controllers.book import get_current_book
from configs import SIGNUP_USER, ADMINISTRATORS

save_path = os.environ.get('save_path')


def add(db_session, data, username):
    logger.info(LogMsg.START, username)

    if username is not SIGNUP_USER and username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    cell_no = data.get('cell_no')
    if cell_no and person_cell_exists(db_session, cell_no):
        raise Http_error(409, LogMsg.PERSON_EXISTS.format('cell_no'))

    email = data.get('email')

    if email and person_mail_exists(db_session, email):
        raise Http_error(409, LogMsg.PERSON_EXISTS.format('email'))

    # logger.info(LogMsg.START,extra={'data':data,'user':username})

    model_instance = Person()
    populate_basic_data(model_instance, username, data.get('tags'))
    model_instance.name = data.get('name')
    model_instance.last_name = data.get('last_name')
    model_instance.address = data.get('address')
    model_instance.phone = data.get('phone')
    model_instance.email = data.get('email')
    model_instance.cell_no = data.get('cell_no')
    model_instance.bio = data.get('bio')
    model_instance.image = data.get('image')

    db_session.add(model_instance)
    add_initial_account(model_instance.id, db_session, username)

    return model_instance


def get(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance:
        person_dict = person_to_dict(model_instance, db_session)
        logger.debug(LogMsg.GET_SUCCESS +
                     json.dumps(person_dict))
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)
    logger.error(LogMsg.GET_FAILED, {"id": id})
    logger.info(LogMsg.END)

    return person_dict


def edit(id, db_session, data, username):
    # TODO: you never checked version of passed data, we have version field in our
    #      records, to prevent conflict when we received two different edit request
    #      concurrently. check KAVEH codes (edit functions) to better understanding
    #      version field usage

    logger.info(LogMsg.START, username)

    if "id" in data.keys():
        del data["id"]
    logger.debug(LogMsg.EDIT_REQUST)

    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance:
        logger.debug(LogMsg.MODEL_GETTING)
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    edit_basic_data(model_instance, username, data.get('tags'))

    logger.debug(LogMsg.MODEL_ALTERED)

    logger.debug(LogMsg.EDIT_SUCCESS, model_to_dict(model_instance))

    logger.info(LogMsg.END)

    return model_instance


def delete(id, db_session, username):
    logger.info(
        LogMsg.START, username)

    logger.info(LogMsg.DELETE_REQUEST, id)

    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'person_id': id})
        raise Http_error(404, Message.NOT_FOUND)
    if person_has_books(id, db_session):
        logger.error(LogMsg.PERSON_HAS_BOOKS)
        raise Http_error(403, Message.PERSON_HAS_BOOKS)

    try:
        delete_person_accounts(id, db_session)
        db_session.delete(model_instance)

        logger.debug(LogMsg.ENTITY_DELETED, {"Person.id {}": id})

        user = db_session.query(User).filter(User.person_id == id).first()

        if user:
            logger.debug(LogMsg.RELATED_USER_DELETE.format(user.id))

            db_session.query(User).filter(User.person_id == id).delete()
            logger.debug(LogMsg.ENTITY_DELETED)
        else:
            logger.debug(LogMsg.NOT_RELATED_USER_FOR_PERSON,
                         {"Person.id {}": id})

    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def get_all(db_session, username):
    logger.info(LogMsg.START + "user is {}".format(username))
    try:
        result = db_session.query(Person).all()
        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logger.debug(LogMsg.END)
    return result


def search_person(data, db_session, username):
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
                raise Http_error(400, Message.MISSING_REQUIERED_FIELD)

            persons = db_session.query(Person).filter(
                or_(Person.name.like('%{}%'.format(person_name)),
                    Person.last_name.like('%{}%'.format(person_name)))
            ).order_by(
                Person.creation_date.desc()).slice(offset,
                                                   offset + limit)

        for person in persons:
            result.append(model_to_dict(person))
    except:
        raise Http_error(404, Message.NOT_FOUND)

    return result


def get_person_profile(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Person).filter(Person.id == id).first()
    if model_instance:
        result = model_to_dict(model_instance)
        result['current_book'] = get_current_book(
            model_instance.current_book_id, db_session) or None
        result['following_list'] = get_following_list_internal(id, db_session)
        result['wish_list'] = internal_wish_list(db_session, Person.id)

        logger.debug(LogMsg.GET_SUCCESS +
                     json.dumps(result))
    else:
        logger.error(LogMsg.GET_FAILED, {"Person.id {}": id})
        raise Http_error(404, Message.NOT_FOUND)
    logger.debug(LogMsg.GET_SUCCESS, json.dumps(result))
    logger.info(LogMsg.END)

    return result


def person_to_dict(person, db_session):
    result = model_basic_dict(person)
    model_attrs = {
        'address': person.address,
        'bio': person.bio,
        'cell_no': person.cell_no,
        'current_book_id': person.current_book_id,
        'email': person.email,
        'image': person.image,
        'name': person.name,
        'last_name': person.last_name,
        'phone': person.phone
        # 'library':library_to_dict(person.library,db_session)

    }
    result.update(model_attrs)
    return result
