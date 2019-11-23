from enums import Permissions
from helper import populate_basic_data
from log import LogMsg, logger
from permission.controllers.permission import check_permission_exists
from permission.models import Permission


def permissions_to_db(db_session,username):
    permissions = Permissions.__members__
    print(permissions)
    result = []
    for permission in permissions:
        if check_permission_exists(permission, db_session):
            pass
        else:
            model_instance = Permission()
            populate_basic_data(model_instance, username)
            logger.debug(LogMsg.POPULATING_BASIC_DATA)
            model_instance.permission = permission
            db_session.add(model_instance)
            result.append(model_instance)

    logger.info(LogMsg.END)
    return result