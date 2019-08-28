
import json
from uuid import uuid4
from app_redis import app_redis as redis

from log import LogMsg,logger
from helper import Now, model_to_dict, Http_error
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_by_username, check_by_cell_no, check_by_id
from user.models import User
from .person import get as get_person , add as add_person, edit as edit_person, get_person_profile


def add(db_session, data,username):
    logger.info(LogMsg.START)
    cell_no = data.get('cell_no')
    name = data.get('name')
    new_username = data.get('username')


    user_by_cell = check_by_cell_no(cell_no,db_session)
    if user_by_cell != None:
        logger.error(LogMsg.USER_XISTS.format(cell_no))
        raise Http_error(409, Message.USER_ALREADY_EXISTS)

    user = check_by_username(new_username,db_session)
    if user:
        logger.error(LogMsg.USER_XISTS.format(new_username))
        raise Http_error(409,Message.USERNAME_EXISTS)

    logger.debug(LogMsg.USR_ADDING)

    model_instance = User()
    model_instance.username = new_username
    model_instance.password = data.get('password')
    model_instance.name = name
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.tags = data.get('tags')


    person_is_valid = None
    person_id = data.get('person_id')
    if person_id:
        person_is_valid = validate_person(person_id,db_session)
        if person_is_valid:
            model_instance.person_id = person_id

        else:
            raise Http_error(404,Message.GET_FAILED)

    logger.debug(LogMsg.DATA_ADDITION)

    db_session.add(model_instance)

    logger.debug(LogMsg.DB_ADD,model_to_dict(model_instance))

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username):
    logger.info(LogMsg.START
                 + "user is {}  ".format(username)
                 + "getting user_id = {}".format(id))
    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(User).filter(User.id == id).first()
    if model_instance:
        result = user_to_dict(model_instance)
        logger.debug(LogMsg.GET_SUCCESS +
                      json.dumps(result))
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": LogMsg.NOT_FOUND})

    logger.error(LogMsg.GET_FAILED + json.dumps({"id": id}))

    logger.info(LogMsg.END)

    return result


def get_profile(username, db_session):
    logger.info(LogMsg.START
                 + "user is {}  ".format(username))
    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(User).filter(User.username == username).first()

    if model_instance:
        profile = get_person_profile(model_instance.person_id,db_session,username)
        logger.debug(LogMsg.GET_SUCCESS +
                      json.dumps(profile))

    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)

    logger.info(LogMsg.END)
    result = model_to_dict(model_instance)
    result['person'] = profile
    del result['password']
    return result


def delete(id, db_session, username):
    logger.info(LogMsg.START + "user is {}  ".format(username)
                 + "user_id= {}".format(id))
    try:
        logger.debug(LogMsg.DELETE_REQUEST +
                      "user_id= {}".format(id))

        db_session.query(User).filter(User.id == id).delete()

        logger.debug(LogMsg.DELETE_SUCCESS)

    except:

        logger.error(LogMsg.DELETE_FAILED +
                      "user_id= {}".format(id))
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logger.info(LogMsg.END)

    return {}


def get_all(db_session, username):
    logger.info(LogMsg.START + "user is {}".format(username))
    logger.debug(LogMsg.GET_ALL_REQUEST + "Users...")
    result = db_session.query(User).all()

    final_res = []
    for item in result:
        final_res.append(user_to_dict(item))

    logger.debug(LogMsg.GET_SUCCESS)


    logger.info(LogMsg.END)

    return final_res


def serach_user(data,db_session, username):
    limit = data.get('limit',10)
    offset = data.get('offset',0)
    filter = data.get('filter',None)
    result = db_session.query(User).filter(User.username !=None).slice(offset, offset + limit)

    final_res = []
    for item in result:
        final_res.append(user_to_dict(item))

    logger.debug(LogMsg.GET_SUCCESS)

    logger.info(LogMsg.END)

    return final_res


def edit(id, db_session, data, username):
    logger.info(LogMsg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
    if "person_id" in data.keys():
        del data["person_id"]
    if 'username' in data.keys():
        raise Http_error(400,{'username':LogMsg.NOT_EDITABLE})

    logger.debug(LogMsg.EDIT_REQUST)

    model_instance = check_by_id(id, db_session)
    if model_instance:
        logger.debug(LogMsg.MODEL_GETTING)
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": LogMsg.NOT_FOUND})



    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    model_instance.modification_date = Now()
    model_instance.modifier = username

    logger.debug(LogMsg.MODEL_ALTERED)

    logger.debug(LogMsg.EDIT_SUCCESS +
                  json.dumps(user_to_dict(model_instance)))

    logger.info(LogMsg.END)

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
    logger.info(LogMsg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
    if "person_id" in data.keys():
        del data["person_id"]
    if ('username' or 'password') in data.keys():
        raise Http_error(400, {'username and password': LogMsg.NOT_EDITABLE})

    logger.debug(LogMsg.EDIT_REQUST)

    user = get(id, db_session, username)
    if user:
        logger.debug(LogMsg.MODEL_GETTING)
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
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"user_id": LogMsg.NOT_FOUND})


    logger.debug(LogMsg.MODEL_ALTERED)

    logger.info(LogMsg.END)

    return user_to_dict(user)


def reset_pass(data,db_session):
    cell_no = data.get('cell_no')
    redis_key = 'PASS_{}'.format(cell_no)
    code = redis.get(redis_key)
    if code is None:
        logger.error(LogMsg.REGISTER_KEY_DOESNT_EXIST)
        raise Http_error(404, Message.INVALID_CODE)

    code = code.decode("utf-8")
    if (code is None) or (code != data.get('code')):
        logger.error(LogMsg.REGISTER_KEY_INVALID)
        raise Http_error(409, Message.INVALID_CODE)

    user = check_by_cell_no(cell_no,db_session)

    if user:
        user.password = data.get('password')
        return {'msg':'successful'}
    raise Http_error(404, Message.INVALID_USER)


