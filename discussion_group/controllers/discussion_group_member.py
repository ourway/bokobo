from discussion_group.models import DiscussionMember
from check_permission import get_user_permissions, has_permission
from enums import Permissions
from helper import Http_error, model_basic_dict, \
    populate_basic_data, edit_basic_data, Http_response, check_schema
from log import LogMsg, logger
from messages import Message
from repository.discussion_group_repo import get_discussion_group, \
    is_admin_member, is_group_member, discuss_group_members, get_groups_by_list
from repository.user_repo import check_user


def add_disscussuion_members(data, db_session, username):
    logger.info(LogMsg.START, username)
    check_schema(['group_id','members'],data.keys())
    group_id = data.get('group_id')
    members = data.get('members')

    group = get_discussion_group(group_id, db_session)
    if group is None:
        logger.error(LogMsg.NOT_FOUND, {'discussion_group_id': group_id})
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)

    is_admin = False
    for item in members:
        if item['person_id']==user.person_id and item['type']=='Admin':
            is_admin = True

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if is_admin or is_admin_member(user.person_id, group_id, db_session) :
        per_data.update({Permissions.IS_OWNER.value: True})

    has_permission([Permissions.DISCUSSION_MEMBER_PREMIUM],
                   permissions, None, per_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    group_members = []

    for item in members:
        member = add(group_id, item.get('person_id'),item.get('type'), db_session, username)
        group_members.append(discussion_member_to_dict(member))
    logger.debug(LogMsg.DISCUSSION_GROUP_MEMBERS_ADDED)
    return group_members


def delete_group_members(group_id, db_session, username):
    logger.info(LogMsg.START, username)
    group = get_discussion_group(group_id, db_session)
    if group is None:
        logger.error(LogMsg.NOT_FOUND, {'discussion_group_id': group_id})
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if is_admin_member(user.person_id, group_id, db_session):
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.DISCUSSION_MEMBER_PREMIUM],permissions, None, per_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    db_session.query(DiscussionMember).filter(
        DiscussionMember.group_id == group_id).delete()

    logger.debug(LogMsg.DISCUSSION_GROUP_OLD_MEMBERS_DELETED)

    return Http_response(204, True)


def add(group_id, person_id, type, db_session, username):
    logger.info(LogMsg.START, username)

    model_instance = DiscussionMember()
    populate_basic_data(model_instance, username)
    logger.debug(LogMsg.POPULATING_BASIC_DATA)

    model_instance.person_id = person_id
    model_instance.group_id = group_id
    model_instance.type = type or 'Normal'

    db_session.add(model_instance)

    return model_instance


def get(id, db_session, username):
    logger.info(LogMsg.START, username)
    result = db_session.query(DiscussionMember).filter(
        DiscussionMember.id == id).first()
    return discussion_member_to_dict(re)


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)
    group_member = get_model(id, db_session)
    if group_member is None:
        logger.error(LogMsg.NOT_FOUND, {'discussion_group_member': id})
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if group_member.person_id == user.person_id or is_admin_member(
            user.person_id, group_member.group_id, db_session):
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.DISCUSSION_MEMBER_PREMIUM],
                   permissions, None, per_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    db_session.query(DiscussionMember).filter(
        DiscussionMember.id == id).delete()

    logger.debug(LogMsg.DISCUSSION_GROUP_OLD_MEMBERS_DELETED)

    return Http_response(204, True)


def edit(id, data, db_session, username):
    logger.info(LogMsg.START, username)
    group_member = get_model(id, db_session)
    if group_member is None:
        logger.error(LogMsg.NOT_FOUND, {'discussion_group_member': id})
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if is_admin_member(user.person_id, group_member.group_id, db_session):
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.DISCUSSION_MEMBER_PREMIUM],
                   permissions, None, per_data)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    for key, value in data.items():
        setattr(group_member, key, value)
    edit_basic_data(group_member, username, data.get('tags'))
    logger.debug(LogMsg.DISCUSSION_GROUP_OLD_MEMBERS_DELETED)

    return discussion_member_to_dict(group_member)


def user_discuss_groups(db_session, username):
    logger.info(LogMsg.START, username)

    user = check_user(username, db_session)
    if user is None:
        logger.error(LogMsg.INVALID_USER, username)
        raise Http_error(404, Message.INVALID_USERNAME)
    group_mems = db_session.query(DiscussionMember).filter(
        DiscussionMember.person_id == user.person_id).all()
    group_ids = []
    for item in group_mems:
        group_ids.append(item.group_id)
    groups = get_groups_by_list(group_ids, db_session)

    logger.info(LogMsg.END)
    return groups


def discussion_member_to_dict(member_model):
    result = {
        'group_id': member_model.group_id,
        'person_id': member_model.person_id,
        'type': member_model.type,

    }
    if member_model.group is not None:
        result['group'] = {
            'title': member_model.group.title,
            'description': member_model.group.description,
            'image': member_model.group.image,
            'status': member_model.group.status
        }
    basic_attrs = model_basic_dict(member_model)
    result.update(basic_attrs)
    return result


def get_model(id, db_session):
    return db_session.query(DiscussionMember).filter(DiscussionMember.id==id).first()
