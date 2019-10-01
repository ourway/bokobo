from group.models import GroupUser


def delete_group_users(group_id,db_session):
    db_session.query(GroupUser).filter(GroupUser.group_id==group_id).delete()
    return True