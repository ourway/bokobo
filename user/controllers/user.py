
import json
import logging
from uuid import uuid4

from log import Msg
from helper import Now, model_to_dict, Http_error, multi_model_to_dict
from repository.person_repo import validate_person
from repository.user_repo import check_by_username, check_by_cell_no, check_by_id
from user.models import User, Person
from .person import get as get_person , add as add_person, edit as edit_person


def add(db_session, data,username):
    logging.info(Msg.START)
    cell_no = data.get('cell_no')
    name = data.get('name')
    new_username = data.get('username')
    user = check_by_username(new_username,db_session)
    if user:
        logging.error(Msg.USER_XISTS.format(new_username))
        raise Http_error(409, {"username": Msg.USER_XISTS.format(new_username)})

    user_by_cell = check_by_cell_no(cell_no,db_session)
    if user_by_cell != None:
        logging.error(Msg.USERNAME_NOT_UNIQUE)
        raise Http_error(409, {"cell_no": Msg.USER_BY_CELL_EXIST})



    logging.debug(Msg.USR_ADDING)

    model_instance = User()
    model_instance.username = new_username
    model_instance.password = data.get('password')
    model_instance.name = name
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username

    person_is_valid = None
    person_id = data.get('person_id')
    if person_id:
        person_is_valid = validate_person(person_id,db_session)
        if person_is_valid:
            model_instance.person_id = person_id

        else:
            raise Http_error(404,Msg.PERSON_NOT_EXISTS.format(person_id))



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
        result = user_to_dict(model_instance)
        logging.debug(Msg.GET_SUCCESS +
                      json.dumps(result))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": Msg.NOT_FOUND})

    logging.error(Msg.GET_FAILED + json.dumps({"id": id}))

    logging.info(Msg.END)

    return result


def get_profile(username, db_session):
    logging.info(Msg.START
                 + "user is {}  ".format(username))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(User).filter(User.username == username).first()

    if model_instance:
        result = user_to_dict(model_instance)
        logging.debug(Msg.GET_SUCCESS +
                      json.dumps(result))

    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"user": Msg.NOT_FOUND})

    logging.info(Msg.END)

    return result


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
    logging.debug(Msg.GET_ALL_REQUEST + "Users...")
    result = db_session.query(User).all()

    final_res = []
    for item in result:
        final_res.append(user_to_dict(item))

    logging.debug(Msg.GET_SUCCESS)


    logging.info(Msg.END)

    return final_res


def edit(id, db_session, data, username):
    logging.info(Msg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
    if "person_id" in data.keys():
        del data["person_id"]
    if 'username' in data.keys():
        raise Http_error(400,{'username':Msg.NOT_EDITABLE})

    logging.debug(Msg.EDIT_REQUST)

    model_instance = check_by_id(id, db_session)
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
                  json.dumps(user_to_dict(model_instance)))

    logging.info(Msg.END)

    return user_to_dict(model_instance)

def user_to_dict(user):
    if not isinstance(user,User):
        raise Http_error(400,Msg.NOT_RIGTH_ENTITY_PASSED.format('USER'))

    result = {
        'username':user.username,
        'creator':user.creator,
        'creation_date': user.creation_date,
        'id':user.id,
        'person_id': user.person_id,
        'person':model_to_dict(user.person),
        'version':user.version,
        'modification_date':user.modification_date,
        'modifier':user.modifier,
        'tags':user.tags
    }

    return result

def edit_profile(id, db_session, data, username):
    logging.info(Msg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
    if "person_id" in data.keys():
        del data["person_id"]
    if ('username' or 'password') in data.keys():
        raise Http_error(400, {'username and password': Msg.NOT_EDITABLE})

    logging.debug(Msg.EDIT_REQUST)

    user = get(id, db_session, username)
    if user:
        logging.debug(Msg.MODEL_GETTING)
        if user.person_id:
            person = get_person(user.person_id,db_session,username)
            if person:
                edit_person(person.id,db_session,data,username)

            else:
                raise Http_error(404,Msg.PERSON_NOT_EXISTS)

        else:
            person = add_person(db_session,data,username)
            user.person_id = person.id

    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"user_id": Msg.NOT_FOUND})


    logging.debug(Msg.MODEL_ALTERED)

    logging.info(Msg.END)

    return user_to_dict(user)