import os

from check_permission import get_user_permissions, has_permission
from discussion_group.controllers.discussion_group_member import \
    add_disscussuion_members, delete_group_members
from enums import Permissions
from helper import model_to_dict, Http_error, model_basic_dict, \
    populate_basic_data, edit_basic_data, Http_response
from log import LogMsg, logger
from messages import Message
from repository.discussion_group_repo import discuss_group_members, \
    is_admin_member, is_group_member
from repository.user_repo import check_user
from ..models import DiscussionGroup

save_path = os.environ.get('save_path')


def add(data, db_session, username):
    logger.info(LogMsg.START, username)

    user = check_user(username, db_session)
    if user is None:
        logger.error(LogMsg.INVALID_USER, username)

    model_instance = DiscussionGroup()
    populate_basic_data(model_instance, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.title = data.get('title')
    model_instance.description = data.get('description')
    model_instance.image = data.get('image')
    model_instance.status = 'Created'

    db_session.add(model_instance)

    members = data.get('members', [])
    members.append({'person_id': user.person_id, 'type': 'Admin'})
    member_data = {'group_id': model_instance.id, 'members': members}

    logger.debug(LogMsg.DISCUSSION_GROUP_ADD, model_to_dict(model_instance))
    discuss_members = add_disscussuion_members(member_data, db_session,
                                               username)
    logger.debug(LogMsg.DISCUSSION_GROUP_MEMBERS_ADDED, members)
    result = model_to_dict(model_instance)
    result['members'] = discuss_members

    logger.info(LogMsg.END)
    return result


def get(id, db_session, username):
    logger.info(LogMsg.START, username)
    user = check_user(username, db_session)
    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if is_group_member(user.person_id, id, db_session):
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.DISCUSSION_GROUP_PREMIUM],
                   permissions, None, per_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    logger.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(DiscussionGroup).filter(
        DiscussionGroup.id == id).first()
    if model_instance:
        result = discuss_group_to_dict(model_instance, db_session)
        logger.debug(LogMsg.GET_SUCCESS, result)
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED, {"discuss_group_id": id})
        raise Http_error(404, Message.NOT_FOUND)
    logger.info(LogMsg.END)

    return result


def edit(id, db_session, data, username):
    logger.info(LogMsg.START, username)

    # TODO: you never checked version of passed data, we have version field in our
    #      records, to prevent conflict when we received two different edit request
    #      concurrently. check KAVEH codes (edit functions) to better understanding
    #      version field usage

    logger.debug(LogMsg.EDIT_REQUST, {'discuss_group_id': id, 'data': data})

    user = check_user(username, db_session)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if is_admin_member(user.person_id, id, db_session):
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.DISCUSSION_GROUP_PREMIUM],
                   permissions, None, per_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    if "id" in data.keys():
        del data["id"]

    model_instance = db_session.query(DiscussionGroup).filter(
        DiscussionGroup.id == id).first()
    if model_instance:
        logger.debug(LogMsg.MODEL_GETTING)
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED, {'discussion_group_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    try:
        for key, value in data.items():
            # TODO  if key is valid attribute of class
            setattr(model_instance, key, value)
        edit_basic_data(model_instance, username, data.get('tags'))
        if 'members' in data:
            members = data.get('members', [])
            members.append({'person_id': user.person_id, 'type': 'Admin'})

            delete_group_members(model_instance.id, db_session, username)
            logger.debug(LogMsg.DISCUSSION_GROUP_OLD_MEMBERS_DELETED)
            member_data = {'group_id': model_instance.id, 'members': members}

            add_disscussuion_members(member_data, db_session, username)
            logger.debug(LogMsg.DISCUSSION_GROUP_MEMBERS_ADDED, members)
        result = discuss_group_to_dict(model_instance, db_session)

        logger.debug(LogMsg.MODEL_ALTERED, result
                     )

    except:
        logger.exception(LogMsg.EDIT_FAILED, exc_info=True)
        raise Http_error(500, Message.EDIT_FAILED)

    logger.info(LogMsg.END)
    return result


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.info(LogMsg.DELETE_REQUEST, {'group_id': id})

    user = check_user(username, db_session)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if is_admin_member(user.person_id, id, db_session):
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.DISCUSSION_GROUP_PREMIUM],
                   permissions, None, per_data)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    model_instance = db_session.query(DiscussionGroup).filter(
        DiscussionGroup.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'group_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    try:
        delete_group_members(model_instance.id, db_session, username)
        logger.debug(LogMsg.DISCUSSION_GROUP_OLD_MEMBERS_DELETED)

        db_session.delete(model_instance)
        logger.debug(LogMsg.DISCUSSION_GROUP_DELETE, id)


    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def get_all(data, db_session, username):
    logger.info(LogMsg.START, username)
    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.DISCUSSION_GROUP_PREMIUM], permissions)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)


    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    try:
        result = DiscussionGroup.mongoquery(
        db_session.query(DiscussionGroup)).query(
        **data).end().all()
        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logger.debug(LogMsg.END)
    return result


def search_group(data, db_session, username=None):

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.DISCUSSION_GROUP_PREMIUM], permissions)
    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    result = []
    groups = DiscussionGroup.mongoquery(
        db_session.query(DiscussionGroup)).query(
        **data).end().all()
    for group in groups:
        result.append(discuss_group_to_dict(group, db_session))
    logger.debug(LogMsg.GET_SUCCESS, result)

    logger.info(LogMsg.END)
    return result


def discuss_group_to_dict(group_model, db_session):
    result = model_to_dict(group_model)
    result['members'] = discuss_group_members(group_model.id, db_session)
    return result
