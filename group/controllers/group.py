import os

from configs import ADMINISTRATORS
from helper import model_to_dict, Http_error, model_basic_dict, \
    populate_basic_data, edit_basic_data, Http_response
from log import LogMsg, logger
from messages import Message
from permission.controllers.group_permission import \
    delete_all_permissions_of_group
from repository.group_repo import check_group_title_exists
from repository.group_user_repo import delete_group_users

from ..models import Group


save_path = os.environ.get('save_path')


def add(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    if check_group_title_exists(data.get('title',None),db_session):
        logger.error(LogMsg.GROUP_EXISTS)
        raise Http_error(409,Message.ALREADY_EXISTS)

    model_instance = Group()
    populate_basic_data(model_instance, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.title = data.get('title')
    db_session.add(model_instance)

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Group).filter(Group.id == id).first()
    if model_instance:
        logger.debug(LogMsg.GET_SUCCESS ,
                     model_to_dict(model_instance))
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)
    logger.error(LogMsg.GET_FAILED, {"id": id})
    logger.info(LogMsg.END)

    return model_instance


def edit(id, db_session, data, username):
    logger.info(LogMsg.START, username)

    # TODO: you never checked version of passed data, we have version field in our
    #      records, to prevent conflict when we received two different edit request
    #      concurrently. check KAVEH codes (edit functions) to better understanding
    #      version field usage

    logger.debug(LogMsg.EDIT_REQUST, {'group_id': id, 'data': data})

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    if "id" in data.keys():
        del data["id"]

    model_instance = db_session.query(Group).filter(Group.id == id).first()
    if model_instance:
        logger.debug(LogMsg.MODEL_GETTING)
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED, {'group_id': id})
        raise Http_error(404, Message.NOT_FOUND)


    try:
        for key, value in data.items():
            # TODO  if key is valid attribute of class
            setattr(model_instance, key, value)
        edit_basic_data(model_instance, username, data.get('tags'))

        logger.debug(LogMsg.MODEL_ALTERED,
                     model_to_dict(model_instance))

    except:
        logger.exception(LogMsg.EDIT_FAILED, exc_info=True)
        raise Http_error(500, Message.DELETE_FAILED)

    logger.info(LogMsg.END)
    return model_instance


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.info(LogMsg.DELETE_REQUEST, {'group_id': id})
    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)


    model_instance = db_session.query(Group).filter(Group.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'group_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    try:
        logger.debug(LogMsg.DELETE_GROUP_USERS,{'group_id': id})
        delete_group_users(model_instance.id, db_session)
        logger.debug(LogMsg.GROUP_DELETE_PERMISSIONS, {'group_id': id})
        delete_all_permissions_of_group(model_instance.id, db_session)
        logger.debug(LogMsg.GROUP_DELETE,id)

        db_session.delete(model_instance)

    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def get_all(data,db_session, username):
    logger.info(LogMsg.START, username)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    try:
        result = Group.mongoquery(db_session.query(Group)).query(**data).end().all()
        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logger.debug(LogMsg.END)
    return result


def search_group(data, db_session,username=None):

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    result = []
    groups = Group.mongoquery(db_session.query(Group)).query(**data).end().all()
    for group in groups:
        result.append(model_to_dict(group))
    logger.debug(LogMsg.GET_SUCCESS, result)

    logger.info(LogMsg.END)
    return result

