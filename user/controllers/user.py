
import json
import logging
import random
from uuid import uuid4

from infrastructure.password_generator import randompassword
from log import LogMsg
from helper import Now, model_to_dict, Http_error, multi_model_to_dict
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_by_username, check_by_cell_no, check_by_id
from send_message.send_message import send_message
from user.models import User
from .person import get as get_person , add as add_person, edit as edit_person, get_person_profile


def add(db_session, data,username):
    logging.info(LogMsg.START)
    cell_no = data.get('cell_no')
    name = data.get('name')
    new_username = data.get('username')


    user_by_cell = check_by_cell_no(cell_no,db_session)
    if user_by_cell != None:
        logging.error(LogMsg.USER_XISTS.format(cell_no))
        raise Http_error(409, Message.MSG1)

    user = check_by_username(new_username,db_session)
    if user:
        logging.error(LogMsg.USER_XISTS.format(new_username))
        raise Http_error(409,Message.MSG8)




    logging.debug(LogMsg.USR_ADDING)

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
            raise Http_error(404,LogMsg.PERSON_NOT_EXISTS.format(person_id))



    logging.debug(LogMsg.DATA_ADDITION)

    db_session.add(model_instance)

    logging.debug(LogMsg.DB_ADD + json.dumps(model_to_dict(model_instance)))

    logging.info(LogMsg.END)
    return model_instance


def get(id, db_session, username):
    logging.info(LogMsg.START
                 + "user is {}  ".format(username)
                 + "getting user_id = {}".format(id))
    logging.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(User).filter(User.id == id).first()
    if model_instance:
        result = user_to_dict(model_instance)
        logging.debug(LogMsg.GET_SUCCESS +
                      json.dumps(result))
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": LogMsg.NOT_FOUND})

    logging.error(LogMsg.GET_FAILED + json.dumps({"id": id}))

    logging.info(LogMsg.END)

    return result


def get_profile(username, db_session):
    logging.info(LogMsg.START
                 + "user is {}  ".format(username))
    logging.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(User).filter(User.username == username).first()

    if model_instance:
        profile = get_person_profile(model_instance.person_id,db_session,username)
        profile['username']=username
        logging.debug(LogMsg.GET_SUCCESS +
                      json.dumps(profile))

    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)

    logging.info(LogMsg.END)

    return profile


def delete(id, db_session, username):
    logging.info(LogMsg.START + "user is {}  ".format(username)
                 + "user_id= {}".format(id))
    try:
        logging.debug(LogMsg.DELETE_REQUEST +
                      "user_id= {}".format(id))

        db_session.query(User).filter(User.id == id).delete()

        logging.debug(LogMsg.DELETE_SUCCESS)

    except:

        logging.error(LogMsg.DELETE_FAILED +
                      "user_id= {}".format(id))
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logging.info(LogMsg.END)

    return {}


def get_all(db_session, username):
    logging.info(LogMsg.START + "user is {}".format(username))
    logging.debug(LogMsg.GET_ALL_REQUEST + "Users...")
    result = db_session.query(User).all()

    final_res = []
    for item in result:
        final_res.append(user_to_dict(item))

    logging.debug(LogMsg.GET_SUCCESS)


    logging.info(LogMsg.END)

    return final_res


def edit(id, db_session, data, username):
    logging.info(LogMsg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
    if "person_id" in data.keys():
        del data["person_id"]
    if 'username' in data.keys():
        raise Http_error(400,{'username':LogMsg.NOT_EDITABLE})

    logging.debug(LogMsg.EDIT_REQUST)

    model_instance = check_by_id(id, db_session)
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
                  json.dumps(user_to_dict(model_instance)))

    logging.info(LogMsg.END)

    return user_to_dict(model_instance)

def user_to_dict(user):
    if not isinstance(user,User):
        raise Http_error(400,LogMsg.NOT_RIGTH_ENTITY_PASSED.format('USER'))

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
    logging.info(LogMsg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
    if "person_id" in data.keys():
        del data["person_id"]
    if ('username' or 'password') in data.keys():
        raise Http_error(400, {'username and password': LogMsg.NOT_EDITABLE})

    logging.debug(LogMsg.EDIT_REQUST)

    user = get(id, db_session, username)
    if user:
        logging.debug(LogMsg.MODEL_GETTING)
        if user.person_id:
            person = get_person(user.person_id,db_session,username)
            if person:
                edit_person(person.id,db_session,data,username)

            else:
                raise Http_error(404,LogMsg.PERSON_NOT_EXISTS)

        else:
            person = add_person(db_session,data,username)
            user.person_id = person.id

    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"user_id": LogMsg.NOT_FOUND})


    logging.debug(LogMsg.MODEL_ALTERED)

    logging.info(LogMsg.END)

    return user_to_dict(user)


def forget_pass(data,db_session):

    username = data.get('username')
    cell_no = data.get('cell_no')

    user = None
    if username:
        user = check_by_username(username, db_session)
    elif cell_no:
        user = check_by_cell_no(cell_no, db_session)
    else:
        raise Http_error(400, Message.USERNAME_CELLNO_REQUIRED)

    if user:
        person = get_person(user.person_id, db_session, username)
        password = randompassword()
        message = 'با کلمه عبور زیر وارد شده و سپس کلمه عبور خود را تغییر دهید n/  {}'.format(password)
        sending_data = {'receptor': person.cell_no, 'message': message}
        send_message(sending_data)
        user.password = password
        return {'msg':'successful'}

    raise Http_error(404,Message.INVALID_USER)



