import os

from configs import ADMINISTRATORS
from helper import model_to_dict, Http_error, model_basic_dict, \
    populate_basic_data, edit_basic_data, Http_response
from log import LogMsg, logger
from messages import Message
from repository.group_repo import validate_groups, validate_group, \
    check_group_title_exists
from repository.user_repo import check_by_id, validate_users
from .group import add as add_group
from ..models import GroupUser

save_path = os.environ.get('save_path')


def add(user_id, group_id, db_session, username):
    logger.info(LogMsg.START, username)

    model_instance = GroupUser()
    populate_basic_data(model_instance, username)
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.group_id = group_id
    model_instance.user_id = user_id

    db_session.add(model_instance)

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(GroupUser).filter(
        GroupUser.id == id).first()
    if model_instance:
        logger.debug(LogMsg.GET_SUCCESS,
                     model_to_dict(model_instance))
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)
    logger.error(LogMsg.GET_FAILED, {"id": id})
    logger.info(LogMsg.END)

    return model_instance


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.info(LogMsg.DELETE_REQUEST, {'group_user_id': id})
    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    model_instance = db_session.query(GroupUser).filter(
        GroupUser.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'group_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    try:
        db_session.delete(model_instance)
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def get_all(db_session, username):
    logger.info(LogMsg.START, username)
    try:
        result = db_session.query(GroupUser).all()
        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logger.debug(LogMsg.END)
    return result


def user_is_in_group(user_id, group_id, db_session):
    result = db_session.query(GroupUser).filter(GroupUser.user_id == user_id,
                                                GroupUser.group_id == group_id).first()
    if result is None:
        return False
    return True


def delete_user_group(user_id, group_id, db_session):
    db_session.query(GroupUser).filter(GroupUser.user_id == user_id,
                                                GroupUser.group_id == group_id).delete()

    return True


def add_users_to_groups(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    users = set(data.get('users'))
    groups = set(data.get('groups'))

    validate_users(users, db_session)
    validate_groups(groups, db_session)
    final_res = {}
    for group_id in groups:
        result = []
        for user_id in users:
            if user_is_in_group(user_id, group_id, db_session):
                logger.error(LogMsg.GROUP_USER_IS_IN_GROUP,
                             {'user_id': user_id, 'group_id': group_id})
                raise Http_error(409, Message.ALREADY_EXISTS)
            result.append(model_to_dict(add(user_id, group_id, db_session, username)))
        final_res.update({group_id:result})

    logger.info(LogMsg.END)
    return final_res


def delete_users_from_groups(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    users = set(data.get('users'))
    groups = set(data.get('groups'))

    validate_users(users, db_session)
    validate_groups(groups, db_session)
    for group_id in groups:
        for user_id in users:
            if not user_is_in_group(user_id, group_id, db_session):
                logger.error(LogMsg.GROUP_USER_NOT_IN_GROUP,
                             {'user_id': user_id, 'group_id': group_id})
                raise Http_error(404, Message.NOT_IN_GROUP)
            delete_user_group(user_id, group_id, db_session)

    logger.info(LogMsg.END)
    return {'result':'successful'}


def add_group_users(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    group_id = data.get('group_id')

    users = data.get('users')


    validate_group(group_id, db_session)
    result = []
    for user_id in users:
        if user_is_in_group(user_id,group_id,db_session):
            logger.error(LogMsg.GROUP_USER_IS_IN_GROUP,
                         {'user_id': user_id, 'group_id': group_id})
            raise Http_error(409, Message.ALREADY_EXISTS)
        result.append(add(user_id, group_id, db_session, username))

    logger.info(LogMsg.END)
    return result


def get_by_group(group_id, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    validate_group(group_id, db_session)
    result = db_session.query(GroupUser).filter(GroupUser.group_id==group_id).all()
    logger.info(LogMsg.END)
    return result

def get_user_groups(user_id, db_session, username):
    logger.info(LogMsg.START, username)

    result = db_session.query(GroupUser).filter(GroupUser.user_id==user_id).all()
    logger.info(LogMsg.END)
    return result


def add_group_by_users(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    users = set(data.get('users'))
    group_title = data.get('title')

    validate_users(users, db_session)
    if check_group_title_exists(group_title,db_session):
        logger.error(LogMsg.GROUP_EXISTS,{'group_title':group_title})
        raise Http_error(409,Message.ALREADY_EXISTS)

    group = add_group({'title':group_title}, db_session, username)
    del data['title']
    data['group_id']=group.id
    result = add_group_users(data, db_session, username)

    return result