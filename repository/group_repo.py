from group.models import Group
from helper import Http_error
from messages import Message


def validate_groups(group_list,db_session):
    result = db_session.query(Group).filter(
        Group.id.in_(set(group_list))).all()
    if (result is not None) and (len(set(group_list)) == len(result)):
        return result
    else:
        raise Http_error(404, Message.INVALID_GROUP)
