from book_rate.controller import get_users_rate
from books.controllers.book import get as get_book
from check_permission import get_user_permissions, has_permission, \
    has_permission_or_not
from comment.controllers.actions import get_comment_like_count, \
    get_comment_reports, liked_by_user, reported_by_user
from comment.models import Comment
from enums import Permissions
from helper import Http_error, model_to_dict, Http_response, value, \
    populate_basic_data, edit_basic_data
from log import LogMsg, logger
from messages import Message
from repository.comment_repo import delete_book_comments, get_comment
from repository.person_repo import validate_person
from repository.user_repo import check_user
from repository.action_repo import delete_comment_actions_internal
from configs import ADMINISTRATORS


def add(db_session, data, username):
    logger.info(LogMsg.START)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    book_id = data.get('book_id')

    logger.debug(LogMsg.COMMENT_VALIDATING_BOOK, book_id)
    book = get_book(book_id, db_session)
    if book is None:
        logger.error(LogMsg.NOT_FOUND, {'book_id': book_id})
        raise Http_error(404, Message.NOT_FOUND)

    logger.debug(LogMsg.CHECK_USER_EXISTANCE, username)
    user = check_user(username, db_session)
    if user is None:
        logger.error(LogMsg.INVALID_USER, username)
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    logger.debug(LogMsg.COMMENT_CHECK_FOR_PARENT)
    parent_id = data.get('parent_id', None)
    if parent_id:
        logger.debug(LogMsg.COMMENT_GETTING_PARENT, parent_id)
        parent_comment = get_comment(parent_id, db_session)
        if parent_comment is None:
            logger.error(LogMsg.COMMENT_PARENT_NOT_FOUND, parent_id)
            raise Http_error(404, Message.PARENT_NOT_FOUND)
        if parent_comment.book_id != book_id:
            logger.error(LogMsg.COMMENT_PARENT_NOT_MATCH, {'book_id': book_id,
                                                           'parent': comment_to_dict(
                                                               db_session,
                                                               parent_comment)})
            raise Http_error(400, Message.ACCESS_DENIED)

    model_instance = Comment()
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    populate_basic_data(model_instance, username, data.get('tags'))
    model_instance.person_id = user.person_id
    model_instance.book_id = book_id
    model_instance.body = data.get('body')
    model_instance.parent_id = data.get('parent_id')

    logger.debug(LogMsg.DATA_ADDITION)

    db_session.add(model_instance)
    logger.debug(LogMsg.DB_ADD)

    logger.info(LogMsg.END)

    return comment_to_dict(db_session, model_instance, username)


def get(id, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)

    try:
        logger.debug(LogMsg.MODEL_GETTING, id)
        result = db_session.query(Comment).filter(Comment.id == id).first()

    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        Http_error(404, Message.NOT_FOUND)

    logger.info(LogMsg.END)

    return comment_to_dict(db_session, result, username)


def delete(id, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING, id)
    model_instance = db_session.query(Comment).filter(Comment.id == id).first()
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

    permission_data = {}
    if model_instance.person_id == user.person_id:
        permission_data.update({Permissions.IS_OWNER.value: True
                                })

    permissions, presses = get_user_permissions(username, db_session)

    has_permission(
        [Permissions.COMMENT_DELETE_PREMIUM],
        permissions, None, permission_data)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        logger.debug(LogMsg.COMMENT_DELETE_ACTIONS, id)
        delete_comment_actions_internal(db_session, id)
        logger.debug(LogMsg.COMMENT_DELETE, id)
        db_session.delete(model_instance)
        logger.debug(LogMsg.DELETE_SUCCESS, {'comment_id': id})
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(404, Message.DELETE_FAILED)
    logger.info(LogMsg.END)

    return Http_response(204, True)


def delete_comments(book_id, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.COMMENT_DELETING_BOOK_COMMENTS, book_id)

    book = get_book(book_id,db_session)
    press = book.get('press',None)

    permissions, presses = get_user_permissions(username, db_session)

    has_permit = has_permission_or_not(
        [Permissions.COMMENT_DELETE_PREMIUM],
        permissions)
    if not has_permit:
        if press in presses:
            has_permission(
                [Permissions.COMMENT_DELETE_PRESS],
                permissions)
        else:
            logger.error(LogMsg.PERMISSION_DENIED,username)
            raise Http_error(403,Message.ACCESS_DENIED)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    delete_book_comments(book_id, db_session)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def get_book_comments(book_id, data, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)
    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    if data.get('filter') is None:
        data.update({'filter':{'book_id':book_id}})
    else:
        data['filter'].update({'person_id':book_id})

    # permissions, presses = get_user_permissions(username, db_session)
    #
    # has_permission(
    #     [Permissions.COMMENT_GET_PREMIUM,Permissions.COMMENT_GET],
    #     permissions)
    #
    # logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        logger.debug(LogMsg.COMMENT_GETTING_BOOK_COMMENTS, book_id)
        res =  Comment.mongoquery(db_session.query(Comment)).query(**data).end().all()
        result = []
        for item in res:
            result.append(comment_to_dict(db_session, item, username))
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(400, Message.NOT_FOUND)
    logger.info(LogMsg.END)

    return result


def get_all(data, db_session, username, **kwargs):
    logger.info(LogMsg.START, username)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']


    permissions, presses = get_user_permissions(username, db_session)

    has_permission_or_not(
        [Permissions.COMMENT_GET_PREMIUM],
        permissions)

    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    try:
        res = Comment.mongoquery(db_session.query(Comment)).query(**data).end().all()
        result = []
        for item in res:
            comment = comment_to_dict(db_session, item, username)
            book = get_book(item.book_id, db_session)
            comment['book'] = book
            result.append(comment)
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(404, Message.NOT_FOUND)
    logger.info(LogMsg.END)
    return result


def edit(id, data, db_session, username):
    logger.info(LogMsg.START, username)

    if "id" in data.keys():
        del data["id"]
        logger.debug(LogMsg.EDIT_REQUST)
    logger.debug(LogMsg.MODEL_GETTING, id)
    model_instance = db_session.query(Comment).filter(Comment.id == id).first()
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
    if model_instance.person_id == user.person_id:
        per_data.update({Permissions.IS_OWNER.value:True})

    has_permission(
        [Permissions.COMMENT_EDIT_PREMIUM],
        permissions,None,per_data)


    logger.debug(LogMsg.PERMISSION_VERIFIED, username)

    if 'person_id' in data:
        del data['person_id']
    if 'book_id' in data:
        del data['book_id']

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)

    edit_basic_data(model_instance, username, data.get('tags'))

    logger.debug(LogMsg.MODEL_ALTERED, id)

    result = comment_to_dict(db_session, model_instance, username)

    logger.debug(LogMsg.EDIT_SUCCESS, result)

    logger.info(LogMsg.END)

    return result


def comment_to_dict(db_session, comment, username):
    logger.info(LogMsg.START, username)
    if not isinstance(comment, Comment):
        raise Http_error(400, Message.INVALID_ENTITY)

    result = {
        'creation_date': comment.creation_date,
        'creator': comment.creator,
        'person_id': comment.person_id,
        'body': comment.body,
        'id': comment.id,
        'modification_date': comment.modification_date,
        'modifier': comment.modifier,
        'parent_id': comment.parent_id,
        'book_id': comment.book_id,
        'version': comment.version,
        'tags': comment.tags,
        'person': model_to_dict(comment.person),
        'likes': get_comment_like_count(comment.id, db_session),
        'reports': len(get_comment_reports(comment.id, db_session)),
        'liked_by_user': liked_by_user(db_session, comment.id, username),
        'reported_by_user': reported_by_user(db_session, comment.id, username),
        'parent': return_parent(comment.parent_id, db_session, username),
        'rate_by_user': get_users_rate(comment.book_id, comment.person_id,
                                       db_session)
    }
    logger.info(LogMsg.END)
    return result


def return_parent(id, db_session, username):
    logger.info(LogMsg.START, username)

    if id is None:
        return None

    comment = db_session.query(Comment).filter(Comment.id == id).first()
    result = {
        'creation_date': comment.creation_date,
        'creator': comment.creator,
        'person_id': comment.person_id,
        'body': comment.body,
        'id': comment.id,
        'modification_date': comment.modification_date,
        'modifier': comment.modifier,
        'parent_id': comment.parent_id,
        'book_id': comment.book_id,
        'version': comment.version,
        'tags': comment.tags,
        'person': model_to_dict(comment.person),
        'likes': get_comment_like_count(comment.id, db_session),
        'reports': len(get_comment_reports(comment.id, db_session)),
        'liked_by_user': liked_by_user(db_session, comment.id, username),
        'reported_by_user': reported_by_user(db_session, comment.id,
                                             username)
    }
    logger.info(LogMsg.END)
    return result
