import json

from enums import Permissions
from helper import Http_error, value
from log import logger, LogMsg
from messages import Message
from permission.controllers.group_permission import \
    get_permission_list_of_groups
from permission.controllers.permission import get_permissions_values
from repository.group_user_repo import get_user_group_list
from repository.user_repo import check_user
from app_redis import app_redis

permission_list_expiration_time = value('permission_list_expiration_time', 60)


def has_permission(func_permissions, user_permission_list, model_instance=None,
                   data=None):
    if any(permission.value in user_permission_list for permission in func_permissions):

        return True
    elif data is not None and data.get(Permissions.IS_OWNER.value,
                                       False) is True:
        return True
    logger.error(LogMsg.NOT_ACCESSED, {'permission': 'not_found'})
    logger.error(LogMsg.PERMISSION_DENIED)
    raise Http_error(403, Message.ACCESS_DENIED)


def has_permission_or_not(func_permissions, user_permission_list, model_instance=None,
                   data=None):
    if any(permission.value in user_permission_list for permission in
           func_permissions):
        return True
    elif data is not None and data.get(Permissions.IS_OWNER.value,
                                       False) is True:
        return True
    logger.error(LogMsg.NOT_ACCESSED, {'permission': 'not_found'})
    logger.error(LogMsg.PERMISSION_DENIED)
    return False


def get_user_permissions(username, db_session):
    user = check_user(username, db_session)

    if user is None:
        logger.error(LogMsg.NOT_FOUND, {'username': username})
        raise Http_error(404, Message.INVALID_USERNAME)
    redis_key = 'PERMISSIONS_{}'.format(user.id)
    permission_list = app_redis.get(redis_key)
    if permission_list is not None:
        data =  json.loads(permission_list.decode("utf-8"))
        return data.get('permission_values',None),data.get('presses',None)

    group_list = get_user_group_list(user.id, db_session)
    if not bool(group_list):
        return [],[]
    permissions = get_permission_list_of_groups(group_list.keys(), db_session)
    permission_values = get_permissions_values(permissions, db_session)

    app_redis.set(redis_key, json.dumps({'permission_values':permission_values,'presses':list(group_list.values())}),
                  ex=permission_list_expiration_time)


    return permission_values,group_list.values()
