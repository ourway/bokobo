from sqlalchemy import or_, and_

from check_permission import get_user_permissions, has_permission
from enums import Permissions
from helper import Http_error, Http_response, \
    populate_basic_data, edit_basic_data, check_schema, Now
from log import LogMsg, logger
from messages import Message
from messaging.controllers.last_seen import update_last_seen, \
    get_receptor_group_last_seen, get_receptor_sender_last_seen
from messaging.models import ChatMessage
from .last_seen import add as add_last_seen
from repository.discussion_group_repo import is_group_member, is_admin_member, \
    user_group_ids
from repository.user_repo import check_user


def add(db_session, data, username):
    logger.info(LogMsg.START, username)

    check_schema(['body'], data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)
    group_id = data.get('group_id', None)
    user = check_user(username, db_session)
    if group_id is not None and not is_group_member(user.person_id, group_id,
                                                    db_session):
        logger.debug(LogMsg.CHAT_PERSON_NOT_IN_GROUP,
                     {'group_id': group_id, 'username': username})
        raise Http_error(403, Message.PERSON_CANT_SENT_MESSAGE)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    parent_id = data.get('parent_id', None)
    if parent_id:
        logger.debug(LogMsg.CHAT_CHECK_FOR_PARENT)
        parent_message = get_internal(parent_id, db_session)
        if parent_message is None:
            logger.error(LogMsg.CHAT_PARENT_NOT_FOUND, parent_id)
            raise Http_error(404, Message.PARENT_NOT_FOUND)

    model_instance = ChatMessage()
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    populate_basic_data(model_instance, username, data.get('tags'))
    model_instance.sender_id = user.person_id
    model_instance.receptor_id = data.get('receptor_id')
    model_instance.group_id = group_id
    model_instance.body = data.get('body')
    model_instance.parent_id = data.get('parent_id')

    db_session.add(model_instance)
    logger.debug(LogMsg.DB_ADD)

    logger.info(LogMsg.END)

    return model_instance


def get(id, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)
    result = None
    user = check_user(username, db_session)

    try:
        logger.debug(LogMsg.MODEL_GETTING, id)
        model_instance = db_session.query(ChatMessage).filter(
            ChatMessage.id == id).first()
        if model_instance.group_id is not None:
            if not is_group_member(user.person_id, model_instance.group_id,
                                   db_session):
                logger.error(LogMsg.CHAT_PERSON_NOT_IN_GROUP, username)
                raise Http_error(403, Message.PERSON_CANT_DELETE_MESSAGE)

        permission_data = {}
        if model_instance.sender_id == user.person_id or \
                model_instance.receptor_id == user.person_id or (
                model_instance.group_id is not None and is_group_member(
            user.person_id, model_instance.group_id, db_session)):
            permission_data.update({Permissions.IS_OWNER.value: True
                                    })

        permissions, presses = get_user_permissions(username, db_session)

        has_permission(
            [Permissions.CHAT_DELETE_PREMIUM],
            permissions, None, permission_data)

        logger.debug(LogMsg.PERMISSION_VERIFIED, username)
        update_last_seen(model_instance, user.person_id, db_session)


    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        Http_error(404, Message.NOT_FOUND)

    logger.info(LogMsg.END)
    return result


def get_internal(id, db_session):
    logger.info(LogMsg.START, '--INTERNAL--')
    return db_session.query(ChatMessage).filter(ChatMessage.id == id).first()


def delete(id, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING, id)
    model_instance = db_session.query(ChatMessage).filter(
        ChatMessage.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, id)
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)
    if user is None:
        logger.error(LogMsg.NOT_FOUND)
        raise Http_error(400, Message.INVALID_USER)
    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)
    if model_instance.group_id is not None:
        if not is_group_member(user.person_id, model_instance.group_id,
                               db_session):
            logger.error(LogMsg.CHAT_PERSON_NOT_IN_GROUP, username)
            raise Http_error(403, Message.PERSON_CANT_DELETE_MESSAGE)

    permission_data = {}
    if model_instance.sender_id == user.person_id or (
            model_instance.group_id is not None and is_admin_member(
        user.person_id, model_instance.group_id, db_session)):
        permission_data.update({Permissions.IS_OWNER.value: True
                                })

    permissions, presses = get_user_permissions(username, db_session)

    has_permission(
        [Permissions.CHAT_DELETE_PREMIUM],
        permissions, None, permission_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        db_session.delete(model_instance)
        logger.debug(LogMsg.DELETE_SUCCESS, {'message_id': id})
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(404, Message.DELETE_FAILED)
    logger.info(LogMsg.END)

    return Http_response(204, True)


def get_group_messages(group_id, data, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)

    limit = data.get('limit', 1000)
    offset = data.get('offset', 0)

    user = check_user(username, db_session)

    permissions, presses = get_user_permissions(username, db_session)
    permission_data = {}
    if is_group_member(user.person_id, group_id, db_session):
        permission_data.update({Permissions.IS_OWNER.value: True})
        seen_data = {'receptor_id': user.person_id, 'group_id': group_id,
                     'last_seen': Now()}
        add_last_seen(seen_data, db_session)
    has_permission([Permissions.CHAT_GET_PREMIUM], permissions, None,
                   permission_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        logger.debug(LogMsg.CHAT_GET_GROUP_MESSAGES, group_id)
        result = db_session.query(ChatMessage).filter(
            ChatMessage.group_id == group_id).order_by(
            ChatMessage.creation_date.desc()).slice(offset, offset + limit)

    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(400, Message.NOT_FOUND)
    logger.info(LogMsg.END)

    return result


def get_sender_messages(sender_id, data, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)
    limit = data.get('limit', 200)
    offset = data.get('offset', 0)

    user = check_user(username, db_session)

    permissions, presses = get_user_permissions(username, db_session)
    permission_data = {Permissions.IS_OWNER.value: True}
    has_permission([Permissions.CHAT_GET_PREMIUM], permissions, None,
                   permission_data)
    seen_data = {'receptor_id': user.person_id, 'sender_id': sender_id,
                 'last_seen': Now()}

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        logger.debug(LogMsg.CHAT_GET_USER_MESSAGES,
                     {'receptor': user.person_id, 'sender': sender_id})
        result = db_session.query(ChatMessage).filter(
            ChatMessage.sender_id == sender_id,
            ChatMessage.receptor_id == user.person_id).order_by(
            ChatMessage.creation_date.desc()).slice(offset, offset + limit)
        add_last_seen(seen_data, db_session)


    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(400, Message.NOT_FOUND)
    logger.info(LogMsg.END)

    return result


def get_user_direct_counts(person_id, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)
    user = check_user(username, db_session)

    permissions, presses = get_user_permissions(username, db_session)
    permission_data = {}
    if user.person_id == person_id:
        permission_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.CHAT_GET_PREMIUM], permissions, None,
                   permission_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        final_res = {}
        logger.debug(LogMsg.CHAT_GET_USER_MESSAGES, person_id)
        result = db_session.query(ChatMessage).filter(and_(
            ChatMessage.receptor_id == person_id,
            ChatMessage.group_id == None)
        ).order_by(
            ChatMessage.creation_date.desc()).all()

        for item in result:
            final_res[item.sender_id] = 0
            seen = get_receptor_sender_last_seen(person_id, item.sender_id,
                                                 db_session)
            if seen.last_seen is None or item.creation_date > seen.last_seen:
                final_res[item.sender_id] += 1

    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(400, Message.NOT_FOUND)
    logger.info(LogMsg.END)

    return final_res


def get_user_group_unread_counts(person_id, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)

    user = check_user(username, db_session)

    permissions, presses = get_user_permissions(username, db_session)
    permission_data = {}
    if user.person_id == person_id:
        permission_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.CHAT_GET_PREMIUM], permissions, None,
                   permission_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    user_groups = user_group_ids(person_id, db_session)
    group_messages = {}

    for group_id in user_groups:
        seen_date = get_receptor_group_last_seen(person_id, group_id,
                                                 db_session)
        if seen_date is None:
            result = db_session.query(ChatMessage).filter(
                ChatMessage.group_id == group_id).order_by(
                ChatMessage.creation_date.desc()).count()
        else:
            result = db_session.query(ChatMessage).filter(
                ChatMessage.group_id == group_id,
                ChatMessage.creation_date > seen_date.last_seen).order_by(
                ChatMessage.creation_date.desc()).count()
        group_messages.update({group_id: result})

    logger.info(LogMsg.END)

    return group_messages

    #
    # def get_user_group_unread_counts(person_id, db_session, username, **kwargs):
    #     logger.info(LogMsg.START, username)
    #
    #     user = check_user(username, db_session)
    #
    #     permissions, presses = get_user_permissions(username, db_session)
    #     permission_data = {}
    #     if user.person_id == person_id:
    #         permission_data.update({Permissions.IS_OWNER.value: True})
    #     has_permission([Permissions.CHAT_GET_PREMIUM], permissions, None,
    #                    permission_data)
    #
    #     logger.debug(LogMsg.PERMISSION_VERIFIED, username)
    #     group_ids = user_group_ids(person_id, db_session)
    #     try:
    #         final_res = {}
    #         for group_id in group_ids:
    #
    #             count = db_session.query(ChatMessage).filter(
    #                 ChatMessage.group_id==group_id,
    #                 ChatMessage.creation_date > from_date).order_by(
    #                 ChatMessage.creation_date.desc()).count()
    #             final_res[group_id] = count
    #     except:
    #         logger.exception(LogMsg.GET_FAILED, exc_info=True)
    #         raise Http_error(400, Message.NOT_FOUND)
    #     logger.info(LogMsg.END)

    return final_res


def get_user_unread_messages(person_id, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)
    groups = get_user_group_unread_counts(person_id, db_session, username)
    directs = get_user_direct_counts(person_id, db_session, username)
    logger.info(LogMsg.END)
    return {'direct': directs, 'groups': groups}


def get_all(data, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)

    limit = data.get('limit') or 10
    offset = data.get('offset') or 0
    filter = data.get('filter') or None

    permissions, presses = get_user_permissions(username, db_session)

    has_permission(
        [Permissions.CHAT_GET_PREMIUM],
        permissions)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        result = db_session.query(ChatMessage).order_by(
            ChatMessage.creation_date.desc()).slice(offset, offset + limit)

    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(404, Message.NOT_FOUND)
    logger.info(LogMsg.END)
    return result


def edit(id, data, db_session, username):
    logger.info(LogMsg.START, username)
    logger.debug(LogMsg.EDIT_REQUST)

    if "id" in data.keys():
        del data["id"]
    logger.debug(LogMsg.MODEL_GETTING, id)
    model_instance = db_session.query(ChatMessage).filter(
        ChatMessage.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.GET_FAILED, id)
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    permissions, presses = get_user_permissions(username, db_session)

    per_data = {}
    if model_instance.sender_id == user.person_id or (
            model_instance.group_id is not None and is_admin_member(
        user.person_id, model_instance.group_id, db_session)):
        per_data.update({Permissions.IS_OWNER.value: True})

    has_permission(
        [Permissions.CHAT_EDIT_PREMIUM],
        permissions, None, per_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    if 'sender_id' in data:
        del data['sender_id']
    if 'group_id' in data:
        del data['group_id']

    for key, value in data.items():
        setattr(model_instance, key, value)

    edit_basic_data(model_instance, username, data.get('tags'))

    logger.debug(LogMsg.MODEL_ALTERED, id)
    logger.info(LogMsg.END)

    return model_instance
