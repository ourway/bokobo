from group.models import Group
from helper import Http_error
from log import logger, LogMsg
from messages import Message


def validate_groups(group_list,db_session):
    result = db_session.query(Group).filter(
        Group.id.in_(set(group_list))).all()
    if (result is not None) and (len(set(group_list)) == len(result)):
        return result
    else:
        raise Http_error(404, Message.INVALID_GROUP)


def validate_group(group_id,db_session):
    group = db_session.query(Group).filter(
        Group.id==group_id).first()
    if group is None:
        logger.error(LogMsg.GROUP_INVALID, {'group_id': group_id})
        raise Http_error(404, Message.INVALID_GROUP)
    return group


def check_group_title_exists(title,db_session):
    result = db_session.query(Group).filter(Group.title==title).first()
    if result is None:
        return False
    return True

