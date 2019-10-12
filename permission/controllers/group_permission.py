from configs import ADMINISTRATORS
from helper import model_to_dict, Http_error, populate_basic_data, \
    Http_response, model_basic_dict
from log import LogMsg, logger
from messages import Message
from permission.controllers.permission import validate_permissions
from repository.group_repo import validate_groups, validate_group
from ..models import GroupPermission


def add(permission_id, group_id, db_session, username):
    logger.info(LogMsg.START, username)

    if group_has_permission(permission_id, group_id, db_session):
        logger.error(LogMsg.PERMISSION_GROUP_ALREADY_HAS)
        raise Http_error(409,Message.ALREADY_EXISTS)

    model_instance = GroupPermission()
    populate_basic_data(model_instance, username)
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.group_id = group_id
    model_instance.permission_id = permission_id

    db_session.add(model_instance)

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(GroupPermission).filter(
        GroupPermission.id == id).first()
    if model_instance:
        logger.debug(LogMsg.GET_SUCCESS,
                     model_to_dict(model_instance))
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)
    logger.error(LogMsg.GET_FAILED, {"id": id})
    logger.info(LogMsg.END)

    return group_permission_to_dict(model_instance)


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.info(LogMsg.DELETE_REQUEST, {'group_permission_id': id})
    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    model_instance = db_session.query(GroupPermission).filter(
        GroupPermission.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'group_permission_id': id})
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
        result = db_session.query(GroupPermission).all()
        logger.debug(LogMsg.GET_SUCCESS)
        final_res = []
        for item in result:
            final_res.append(group_permission_to_dict(item))
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logger.info(LogMsg.END)
    return final_res


def group_has_permission(permission_id, group_id, db_session):
    result = db_session.query(GroupPermission).filter(
        GroupPermission.permission_id == permission_id,
        GroupPermission.group_id == group_id).first()
    if result is None:
        return False
    return True


def delete_permission_for_group(permission_id, group_id, db_session):
    db_session.query(GroupPermission).filter(
        GroupPermission.permission_id == permission_id,
        GroupPermission.group_id == group_id).delete()
    return True


def add_permissions_to_groups(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    permissions = set(data.get('permissions'))
    groups = set(data.get('groups'))

    validate_permissions(permissions, db_session)
    validate_groups(groups, db_session)
    final_res = {}
    for group_id in groups:
        result = []
        for permission_id in permissions:
            if group_has_permission(permission_id, group_id, db_session):
                logger.error(LogMsg.PERMISSION_GROUP_ALREADY_HAS,
                             {'permission_id': permission_id,
                              'group_id': group_id})
                raise Http_error(409, Message.ALREADY_EXISTS)
            result.append(group_permission_to_dict(
                add(permission_id, group_id, db_session, username)))
        final_res.update({group_id: result})

    logger.info(LogMsg.END)
    return final_res


def delete_permissions_of_groups(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    permissions = set(data.get('permissions'))
    groups = set(data.get('groups'))

    validate_permissions(permissions, db_session)
    validate_groups(groups, db_session)
    for group_id in groups:
        for permission_id in permissions:
            if not group_has_permission(permission_id, group_id, db_session):
                logger.error(LogMsg.PERMISSION_NOT_HAS_GROUP,
                             {'permission_id': permission_id,
                              'group_id': group_id})
                raise Http_error(404, Message.PERMISSION_NOT_FOUND)
            delete_permission_for_group(permission_id, group_id, db_session)

    logger.info(LogMsg.END)
    return {'result': 'successful'}


def add_group_permissions(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    group_id = data.get('group_id')
    permissions = data.get('permissions')

    validate_group(group_id, db_session)
    result = []
    for permission_id in permissions:
        if group_has_permission(permission_id, group_id, db_session):
            logger.error(LogMsg.GROUP_USER_IS_IN_GROUP,
                         {'permission_id': permission_id, 'group_id': group_id})
            raise Http_error(409, Message.ALREADY_EXISTS)
        result.append(
            group_permission_to_dict(add(permission_id, group_id, db_session, username)))

    logger.info(LogMsg.END)
    return result


def delete_group_permissions(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    group_id = data.get('group_id')
    permissions = data.get('permissions')

    validate_group(group_id, db_session)
    result = []
    for permission_id in permissions:
        if not group_has_permission(permission_id, group_id, db_session):
            logger.error(LogMsg.PERMISSION_NOT_HAS_GROUP,
                         {'permission_id': permission_id, 'group_id': group_id})
            raise Http_error(404, Message.PERMISSION_NOT_FOUND)
        delete_permission_for_group(permission_id, group_id, db_session, username)

    logger.info(LogMsg.END)
    return result


def get_by_data(data, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    offset = data.get('offset', 0)
    limit = data.get('limit', 20)
    filter = data.get('filter', None)

    result = []
    if filter is None:
        permissions = db_session.query(GroupPermission).order_by(
            GroupPermission.creation_date.desc()).slice(offset,
                                                        offset + limit)

    else:
        permission = filter.get('permission', None)
        if permission is not None:
            permissions = db_session.query(GroupPermission).filter(
                GroupPermission.permission_id == permission).order_by(
                GroupPermission.creation_date.desc()).slice(offset,
                                                            offset + limit)
        group = filter.get('group', None)
        if group is not None:
            permissions = db_session.query(GroupPermission).filter(
                GroupPermission.group_id == group).order_by(
                GroupPermission.creation_date.desc()).slice(offset,
                                                            offset + limit)
    for permission in permissions:
        result.append(group_permission_to_dict(permission))
    logger.debug(LogMsg.GET_SUCCESS, result)

    logger.info(LogMsg.END)
    return result


def get_by_permission(permission_id, db_session, username):
    logger.info(LogMsg.START, username)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, {'username': username})
        raise Http_error(403, Message.ACCESS_DENIED)

    result = db_session.query(GroupPermission).filter(
        GroupPermission.permission_id == permission_id).all()
    final_res = []
    for item in result:
        final_res.append(group_permission_to_dict(item))
    logger.info(LogMsg.END)
    return final_res


def delete_all_permissions_of_group(group_id,db_session):
    db_session.query(GroupPermission).filter(GroupPermission.group_id==group_id).delete()
    return True


def get_permission_list_of_groups(group_list,db_session):
    groups = set(group_list)
    result = db_session.query(GroupPermission).filter(GroupPermission.group_id.in_(groups)).all()

    permissions = []
    for item in result:
        permissions.append(item.permission_id)
    return set(permissions)

def group_permission_list(data,db_session,username):
    logger.info(LogMsg.START,username)
    groups = data.get('groups',None)
    result = db_session.query(GroupPermission).filter(
        GroupPermission.group_id.in_(groups)).all()

    permissions = []
    for item in result:
        permissions.append(group_permission_to_dict(item))
    logger.info(LogMsg.END)
    return permissions


def group_permission_to_dict(model_instance):
    result = {
        'group_id':model_instance.group_id,
        'permission_id': model_instance.permission_id,
        'permission':model_to_dict(model_instance.permission)
    }
    primary_data = model_basic_dict(model_instance)
    result.update(primary_data)
    return result