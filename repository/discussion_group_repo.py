from discussion_group.models import DiscussionMember, DiscussionGroup
from helper import model_basic_dict
from repository.person_repo import get_persons


def discuss_group_members(group_id, db_session):
    result = db_session.query(DiscussionMember).filter(
        DiscussionMember.group_id == group_id).all()
    members =[]
    for member in result:
        members.append(member.person_id)
    persons = get_persons(members, db_session)
    return persons


def is_admin_member(person_id, group_id, db_session):
    member = db_session.query(DiscussionMember).filter(
        DiscussionMember.group_id == group_id,DiscussionMember.person_id==person_id).first()
    if member is not None and member.type=='Admin':
        return True
    return False


def get_discussion_group(group_id,db_session):
    return db_session.query(DiscussionGroup).filter(DiscussionGroup.id==group_id).first()


def is_group_member(person_id, group_id, db_session):
    member = db_session.query(DiscussionMember).filter(
        DiscussionMember.group_id == group_id,DiscussionMember.person_id==person_id).first()
    if member is not None and member is None:
        return False
    return True


def get_groups_by_list(group_ids,db_session):
    groups = db_session.query(DiscussionGroup).filter(
        DiscussionGroup.id.in_(group_ids)).all()
    result = []
    for group in groups:
        group_dict = {
            'title':group.title,
            'description':group.description,
            'status':group.status,
            'image':group.image
        }
        basics = model_basic_dict(group)
        group_dict.update(basics)
        result.append(group_dict)
    return result


def user_group_ids(person_id, db_session):

    group_mems = db_session.query(DiscussionMember).filter(
        DiscussionMember.person_id == person_id).all()
    group_ids = []
    for item in group_mems:
        group_ids.append(item.group_id)
    return group_ids
