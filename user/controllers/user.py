import json
from uuid import uuid4
from app_redis import app_redis as redis
from check_permission import get_user_permissions, has_permission, \
    has_permission_or_not
from configs import ADMINISTRATORS
from enums import Permissions

from log import LogMsg, logger
from helper import Now, model_to_dict, Http_error, edit_basic_data, \
    populate_basic_data, Http_response
from messages import Message
from repository.group_user_repo import delete_user_from_groups
from repository.person_repo import validate_person
from repository.user_repo import check_by_username, check_by_cell_no, \
    check_by_id
from user.models import User
from .person import get as get_person, add as add_person, edit as edit_person, \
    get_person_profile


def add(db_session, data, username):
    logger.info(LogMsg.START)
    cell_no = data.get('cell_no')
    name = data.get('name')
    new_username = data.get('username')

    user = check_by_username(new_username, db_session)
    if user:
        logger.error(LogMsg.USER_XISTS, new_username)
        raise Http_error(409, Message.USERNAME_EXISTS)

    logger.debug(LogMsg.USR_ADDING)

    model_instance = User()
    model_instance.username = new_username
    model_instance.password = data.get('password')
    model_instance.name = name
    populate_basic_data(model_instance, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    person_id = data.get('person_id')
    if person_id:
        person_is_valid = validate_person(person_id, db_session)
        logger.debug(LogMsg.PERSON_EXISTS, {'person_id': person_id})
        if person_is_valid:
            model_instance.person_id = person_id

        else:
            logger.error(LogMsg.INVALID_USER, {'person_id': person_id})
            raise Http_error(404, Message.INVALID_USER)

    db_session.add(model_instance)

    logger.debug(LogMsg.DB_ADD, model_to_dict(model_instance))

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING, {'user_id': id})
    model_instance = db_session.query(User).filter(User.id == id).first()
    if model_instance:
        result = user_to_dict(model_instance)
        logger.debug(LogMsg.GET_SUCCESS, result)
    else:
        logger.debug(LogMsg.NOT_FOUND, {'user_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    logger.error(LogMsg.GET_FAILED, {'user_id': id})
    logger.info(LogMsg.END)

    return result


def get_profile(username, db_session):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING, {'user.username': username})
    model_instance = db_session.query(User).filter(
        User.username == username).first()

    if model_instance:
        profile = get_person_profile(model_instance.person_id, db_session,
                                     username)
        permissions,groups = get_user_permissions(username, db_session)
        logger.debug(LogMsg.GET_SUCCESS, profile)

    else:
        logger.debug(LogMsg.NOT_FOUND, {'user.username': username})
        raise Http_error(404, Message.NOT_FOUND)

    result = model_to_dict(model_instance)
    result['person'] = profile
    result['permissions'] = permissions
    result['permission_groups'] = groups

    del result['password']
    logger.debug(LogMsg.USER_PROFILE_IS, result)
    logger.info(LogMsg.END)

    return result


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)
    user = db_session.query(User).filter(User.id == id).first()
    if user is None:
        logger.error(LogMsg.NOT_FOUND,{'user_id':id})
        raise Http_error(404,Message.NOT_FOUND)
    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if user.username == username:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.USER_DELETE_PREMIUM],
                   permissions, None, per_data)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    try:
        logger.debug(LogMsg.DELETE_REQUEST, {'user_id': id})
        logger.debug(LogMsg.GROUP_DELETE_USER_GROUPS, id)
        delete_user_from_groups(id, db_session)
        db_session.delete(user)

        logger.debug(LogMsg.DELETE_SUCCESS, {'user_id': id})

    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, LogMsg.DELETE_FAILED)
    logger.info(LogMsg.END)

    return {}


def get_all(db_session, username):
    logger.info(LogMsg.START, username)
    logger.debug(LogMsg.GET_ALL_REQUEST, "Users...")
    result = db_session.query(User).order_by(User.creation_date.desc()).all()

    permissions, presses = get_user_permissions(username, db_session)

    has_permission([Permissions.USER_GET_PREMIUM],
                   permissions)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    final_res = []
    for item in result:
        final_res.append(user_to_dict(item))

    logger.debug(LogMsg.GET_SUCCESS, final_res)
    logger.info(LogMsg.END)

    return final_res


def serach_user(data, db_session, username):
    logger.info(LogMsg.START, username)

    permissions, presses = get_user_permissions(username, db_session)

    has_permission([Permissions.USER_GET_PREMIUM],
                   permissions)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    limit = data.get('limit', 10)
    offset = data.get('offset', 0)
    filter = data.get('filter', None)
    if filter is None:
        result = db_session.query(User).filter(User.username != None).order_by(
            User.creation_date.desc()).slice(offset, offset + limit)
    else:
        search_username = filter.get('username')
        logger.debug(LogMsg.USER_GET_BY_FILTER, {'username': search_username})

        result = db_session.query(User).filter(
            User.username.like('%{}%'.format(search_username))).order_by(
            User.creation_date.desc()).slice(
            offset, offset + limit)
    final_res = []
    for item in result:
        final_res.append(user_to_dict(item))

    logger.debug(LogMsg.GET_SUCCESS, final_res)
    logger.info(LogMsg.END)

    return final_res


def edit(id, db_session, data, username):
    logger.info(LogMsg.START, username)
    if "id" in data.keys():
        del data["id"]
    if 'username' in data.keys():
        logger.error(LogMsg.NOT_EDITABLE, 'username')
        raise Http_error(400, Message.NOT_EDITABLE)

    logger.debug(LogMsg.EDIT_REQUST, {'user_id': id, 'data': data})

    model_instance = check_by_id(id, db_session)
    if model_instance:
        logger.debug(LogMsg.MODEL_GETTING, {'user_id': id})
    else:
        logger.debug(LogMsg.NOT_FOUND, {'user_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if model_instance.username == username:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.USER_EDIT_PREMIUM],
                   permissions, None, per_data)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    if not has_permission_or_not([Permissions.USER_EDIT_PREMIUM],
                   permissions):
        if "person_id" in data:
            del data["person_id"]
    # if "person_id" in data:
    #     user_by_person = db_session.query(User).filter(
    #         User.person_id == data.get('person_id')).first()
    #     if user_by_person is not None and user_by_person.id != model_instance.id:
    #         raise Http_error(409,Message.USER_ALREADY_EXISTS)
    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    edit_basic_data(model_instance, username, data.get('tags'))
    user_dict = user_to_dict(model_instance)

    logger.debug(LogMsg.EDIT_SUCCESS, user_dict)
    logger.info(LogMsg.END)

    return user_dict


def user_to_dict(user):
    if not isinstance(user, User):
        raise Http_error(400, LogMsg.NOT_RIGTH_ENTITY_PASSED.format('USER'))

    result = {
        'username': user.username,
        'creator': user.creator,
        'creation_date': user.creation_date,
        'id': user.id,
        'person_id': user.person_id,
        'person': model_to_dict(user.person),
        'version': user.version,
        'modification_date': user.modification_date,
        'modifier': user.modifier,
        'tags': user.tags
    }

    return result


def edit_profile(id, db_session, data, username):
    logger.info(LogMsg.START, username)
    if "id" in data.keys():
        del data["id"]
    if "person_id" in data.keys():
        del data["person_id"]
    if ('username' or 'password') in data.keys():
        logger.error(LogMsg.NOT_EDITABLE, 'username , password')
        raise Http_error(400, Message.NOT_EDITABLE)

    logger.debug(LogMsg.EDIT_REQUST, data)

    user = get(id, db_session, username)
    if user:
        logger.debug(LogMsg.MODEL_GETTING, {'user_id': id})
        if user.person_id:
            person = get_person(user.person_id, db_session, username)
            logger.debug(LogMsg.PERSON_EXISTS, username)
            per_data = {}
            permissions, presses = get_user_permissions(username, db_session)
            if user['username'] == username:
                per_data.update({Permissions.IS_OWNER.value: True})
            has_permission([Permissions.USER_EDIT_PREMIUM],
                           permissions, None, per_data)
            logger.debug(LogMsg.PERMISSION_VERIFIED)

            if person:
                edit_person(person.id, db_session, data, username)

            else:
                logger.error(LogMsg.USER_HAS_NO_PERSON, username)
                raise Http_error(404, LogMsg.PERSON_NOT_EXISTS)

        else:
            del data['current_book']
            person = add_person(db_session, data, username)
            user.person_id = person.id

    else:
        logger.debug(LogMsg.NOT_FOUND, {'user_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    user_dict = user_to_dict(user)
    logger.debug(LogMsg.MODEL_ALTERED, user_dict)

    logger.info(LogMsg.END)

    return user_dict


def reset_pass(data, db_session):
    logger.info(LogMsg.START, data)

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

    user = check_by_cell_no(cell_no, db_session)

    if user:
        user.password = data.get('password')

        logger.debug(LogMsg.USER_PASSWORD_RESET, user_to_dict(user))
        logger.info(LogMsg.END)

        return data

    logger.error(LogMsg.NOT_FOUND, data)
    raise Http_error(404, Message.INVALID_USER)
