import os
from configs import ADMINISTRATORS
from helper import model_to_dict, Http_error, model_basic_dict, \
    populate_basic_data, edit_basic_data, Http_response
from log import LogMsg, logger
from messages import Message
from permission.models import Permission


def add(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    if check_permission_exists(data.get('permission'),db_session):
        raise Http_error(409,Message.ALREADY_EXISTS)
    model_instance = Permission()
    populate_basic_data(model_instance, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.permission = data.get('permission')
    model_instance.description = data.get('description')
    db_session.add(model_instance)

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Permission).filter(Permission.id == id).first()
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

    logger.debug(LogMsg.EDIT_REQUST, {'permission_id': id, 'data': data})

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    if "id" in data.keys():
        del data["id"]

    model_instance = db_session.query(Permission).filter(Permission.id == id).first()
    if model_instance:
        logger.debug(LogMsg.MODEL_GETTING)
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED, {'permission_id': id})
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

    logger.info(LogMsg.DELETE_REQUEST, {'permission_id': id})
    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)


    model_instance = db_session.query(Permission).filter(Permission.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'permission_id': id})
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
        result = db_session.query(Permission).all()
        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logger.debug(LogMsg.END)
    return result


def search_permission(data, db_session,username=None):
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)
    filter = data.get('filter', None)

    result = []
    if filter is None:
        permissions = db_session.query(Permission).order_by(
            Permission.creation_date.desc()).slice(offset,
                                              offset + limit)

    else:
        title = filter.get('permission')
        if title is None:
            raise Http_error(400, Message.MISSING_REQUIERED_FIELD)
        permissions = db_session.query(Permission).filter(
            Permission.permission.like('%{}%'.format(title))).order_by(
            Permission.creation_date.desc()).slice(offset,
                                              offset + limit)
    for permission in permissions:
        result.append(model_to_dict(permission))
    logger.debug(LogMsg.GET_SUCCESS, result)

    logger.info(LogMsg.END)
    return result


def validate_permissions(permission_list, db_session):
    result = db_session.query(Permission).filter(
        Permission.id.in_(set(permission_list))).all()
    if (result is not None) and (len(set(permission_list)) == len(result)):
        return result
    else:
        raise Http_error(404, Message.INVALID_GROUP)


def check_permission_exists(permission, db_session):
    result = db_session.query(Permission).filter(
        Permission.permission==permission).first()
    if result is None:
        return False
    return True


def get_permissions_values(permission_list,db_session):
    result = db_session.query(Permission).filter(
        Permission.id.in_(set(permission_list))).all()
    permission_values = []
    for item in result:
        permission_values.append(item.permission)
    return permission_values