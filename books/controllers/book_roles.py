import json
import logging

from enums import Roles, check_enums, str_role
from helper import Now, Http_error, model_to_dict
from log import LogMsg
from messages import Message
from repository.person_repo import validate_persons
from ..models import BookRole
from uuid import uuid4


def add(db_session,data,username):

    model_instance = BookRole()
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    model_instance.tags = data.get('tags')
    model_instance.person_id = data.get('person_id')
    model_instance.book_id = data.get('book_id')
    model_instance.role = data.get('role')

    db_session.add(model_instance)

    return model_instance

def add_book_roles(book_id,roles_dict_list,db_session,username):
    result = []
    role_person={}

    for item in roles_dict_list:
        person = item.get('person')
        role_person.update({item.get('role'):person.get('id')})
    check_enums(role_person.keys(), Roles)

    validate_persons(role_person.values(),db_session)

    elastic_data = {'persons': list(role_person.values())}

    for role,person_id in role_person.items():
        data = {'role':role,
                'book_id':book_id,
                'person_id':person_id}
        if role =='Writer':
            elastic_data['Writer'] = person_id
        elif role == 'Press':
            elastic_data['Press'] = person_id

        book_role = add(db_session,data,username)
        result.append(book_role)

    return result, elastic_data


def get(id, db_session):
    logging.info(LogMsg.START)
    logging.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(BookRole).filter(BookRole.id == id).first()
    if model_instance:

        logging.debug(LogMsg.GET_SUCCESS +
                      json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": LogMsg.NOT_FOUND})

    logging.error(LogMsg.GET_FAILED + json.dumps({"id": id}))

    logging.info(LogMsg.END)

    return model_instance


def edit(db_session, data, username):
    logging.info(LogMsg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
        logging.debug(LogMsg.EDIT_REQUST)

    model_instance = db_session.query(BookRole).filter(BookRole.id == id).first()
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
    model_instance.version += 1

    logging.debug(LogMsg.MODEL_ALTERED)

    logging.debug(LogMsg.EDIT_SUCCESS +
                  json.dumps(model_to_dict(model_instance)))

    logging.info(LogMsg.END)

    return model_instance


def delete(id, db_session, username):
    logging.info(LogMsg.START + "user is {}  ".format(username) + "book_id = {}".format(id))

    logging.info(LogMsg.DELETE_REQUEST + "user is {}".format(username))

    try:
        db_session.query(BookRole).filter(BookRole.id == id).delete()

        logging.debug(LogMsg.ENTITY_DELETED + "book_role.id {}".format(id))

    except:
        logging.error(LogMsg.DELETE_FAILED)
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logging.info(LogMsg.END)
    return {}


def get_all(db_session):
    logging.info(LogMsg.START )
    try:
        result = db_session.query(BookRole).all()
        logging.debug(LogMsg.GET_SUCCESS)

    except:
        logging.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logging.debug(LogMsg.END)
    return result

def get_book_roles(book_id,db_session):
    logging.info(LogMsg.START )

    try:
        result = db_session.query(BookRole).filter(BookRole.book_id==book_id).all()
        logging.debug(LogMsg.GET_SUCCESS)


    except:
        logging.error(LogMsg.GET_FAILED)
        raise Http_error(500, Message.MSG14)

    logging.debug(LogMsg.END)
    return result


def delete_book_roles(book_id,db_session):
    logging.info(LogMsg.START)

    try:
        db_session.query(BookRole).filter(BookRole.book_id == book_id).delete()
        logging.debug(LogMsg.GET_SUCCESS)


    except:
        logging.error(LogMsg.GET_FAILED)
        raise Http_error(500, Message.MSG13)

    logging.debug(LogMsg.END)
    return {'status':'successful'}

def append_book_roles_dict(book_id,db_session):
    result = []
    roles = get_book_roles(book_id,db_session)
    for role in roles:
        result.append(book_role_to_dict(role))

    return result

def book_role_to_dict(obj):
    if not isinstance(obj, BookRole):
        raise Http_error(500, LogMsg.NOT_RIGTH_ENTITY_PASSED.format('BookRole'))

    result = {
        'creation_date': obj.creation_date,
        'creator': obj.creator,
        'id': obj.id,
        'modification_date': obj.modification_date,
        'modifier': obj.modifier,
        'person':model_to_dict(obj.person),
        'tags': obj.tags,
        'version': obj.version
    }

    if isinstance(obj.role,str):
        result['role'] = obj.role
    else:
        result['role'] = obj.role.name

    return result


def books_by_person(person_id,db_session):
    result = db_session.query(BookRole.book_id).filter(BookRole.person_id == person_id).all()
    final_res = []
    for item in result:
        final_res.append(item.book_id)
    return final_res