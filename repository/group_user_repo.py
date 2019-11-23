from group.models import GroupUser
from repository.group_repo import validate_groups


def delete_group_users(group_id,db_session):
    db_session.query(GroupUser).filter(GroupUser.group_id==group_id).delete()
    return True

def delete_user_from_groups(user_id,db_session):
    db_session.query(GroupUser).filter(GroupUser.user_id==user_id).delete()
    return True

def get_user_group_list(user_id,db_session):
    result = db_session.query(GroupUser).filter(
        GroupUser.user_id == user_id).all()

    groups = []
    for item in result:
        groups.append(item.group_id)
    group_persons_list = validate_groups(groups,db_session)
    group_persons = {}
    for item in group_persons_list:
        group_persons.update({item.id:item.person_id})
    return group_persons


def users_of_groups(group_list,db_session):

    group_users = db_session.query(GroupUser).filter(GroupUser.group_id.in_(group_list)).all()

    users = []
    for item in group_users:
        users.append(item.user_id)

    result = set(users)
    return result