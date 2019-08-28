from sqlalchemy import and_

from repository.comment_repo import get_comment
from comment.models import CommentAction
from enums import ReportComment, check_enum
from helper import Http_error, model_to_dict, populate_basic_data, Http_response
from log import LogMsg, logger
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user


def add(db_session, data, username):
    logger.info(LogMsg.START, username)

    report = data.get('report', None)
    if report:
        logger.debug(LogMsg.ENUM_CHECK, {'report_comment': report})
        check_enum(report, ReportComment)

    comment_id = data.get('comment_id')
    logger.debug(LogMsg.ACTION_CHECK_COMMENT, comment_id)
    comment = get_comment(comment_id, db_session)
    if comment is None:
        logger.error(LogMsg.NOT_FOUND, {'comment_id': comment_id})
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    logger.debug(LogMsg.CHECK_USER_EXISTANCE)
    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    model_instance = CommentAction()

    populate_basic_data(model_instance, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.comment_id = comment_id
    model_instance.person_id = user.person_id
    model_instance.like = data.get('like')
    model_instance.report = report

    db_session.add(model_instance)
    logger.debug(LogMsg.DB_ADD)
    logger.info(LogMsg.END)

    return model_instance


def like(db_session, comment_id, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.ACTION_CHECK_COMMENT, comment_id)
    comment = get_comment(comment_id, db_session)
    if comment is None:
        logger.error(LogMsg.NOT_FOUND, comment_id)
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)
    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    logger.debug(LogMsg.ACTION_CHECK_USER_LIKED, comment_id)
    action = get_action_like(comment_id, user.person_id, db_session)
    if action is not None:
        logger.error(LogMsg.ACTION_ALREADY_LIKED)
        raise Http_error(409, Message.ALREADY_LIKED)

    logger.debug(LogMsg.ACTION_LIKE_COMMENT, comment_id)

    model_instance = CommentAction()

    populate_basic_data(model_instance, username, None)
    model_instance.comment_id = comment_id
    model_instance.person_id = user.person_id
    model_instance.like = True

    db_session.add(model_instance)
    logger.debug(LogMsg.DB_ADD)
    logger.info(LogMsg.END)

    return model_instance


def dislike(db_session, comment_id, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.ACTION_CHECK_COMMENT, comment_id)
    comment = get_comment(comment_id, db_session)
    if comment is None:
        logger.error(LogMsg.NOT_FOUND, {'comment_id': comment_id})
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    action = get_action_like(comment_id, user.person_id, db_session)
    if action is None:
        logger.error(LogMsg.ACTION_USER_CANT_DISLIKE)
        raise Http_error(404, Message.COMMENT_NOT_FOUND)

    if action.person_id != user.person_id:
        logger.error(LogMsg.NOT_ACCESSED, username)
        raise Http_error(403, Message.ACCESS_DENIED)

    logger.debug(LogMsg.ACTION_DISLIKE_COMMENT, comment_id)
    delete(action.id, db_session, username)
    logger.info(LogMsg.END)

    return Http_response(204, True)


def report(db_session, comment_id, data, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.ACTION_CHECK_COMMENT, comment_id)
    comment = get_comment(comment_id, db_session)
    if comment is None:
        logger.error(LogMsg.NOT_FOUND, {'comment_id', comment_id})
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    logger.debug(LogMsg.ACTION_CHECK_USER_REPORTED, comment_id)
    action = get_action_report(comment_id, user.person_id, db_session)
    if action is not None:
        logger.error(LogMsg.ACTION_ALREADY_REPORTED, comment_id)
        raise Http_error(409, Message.ALREADY_REPORTED)

    report = data.get('report', None)
    if report:
        logger.debug(LogMsg.ENUM_CHECK, {'report': report})
        check_enum(report, ReportComment)

    model_instance = CommentAction()

    populate_basic_data(model_instance, username, None)
    model_instance.comment_id = comment_id
    model_instance.person_id = user.person_id
    model_instance.report = report

    db_session.add(model_instance)
    logger.debug(LogMsg.DB_ADD)
    logger.info(LogMsg.END)
    return model_instance


def dis_report(db_session, comment_id, username):
    logger.info(LogMsg.START, username)
    logger.debug(LogMsg.ACTION_CHECK_COMMENT, comment_id)
    comment = get_comment(comment_id, db_session)
    if comment is None:
        logger.error(LogMsg.NOT_FOUND)
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    logger.debug(LogMsg.ACTION_CHECK_USER_REPORTED)
    action = get_action_report(comment_id, user.person_id, db_session)
    if action is None:
        logger.error(LogMsg.ACTION_USER_CANT_DISREPORT)
        raise Http_error(404, Message.REPORT_NOT_FOUND)

    if action.person_id != user.person_id:
        logger.error(LogMsg.NOT_ACCESSED, username)
        raise Http_error(403, Message.ACCESS_DENIED)

    logger.debug(LogMsg.ACTION_DISREPORT_COMMENT, comment_id)
    delete(action.id, db_session, username)
    logger.info(LogMsg.END)

    return {}


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.MODEL_GETTING, {'comment_action_id': id})
    action = db_session.query(CommentAction).filter(
        CommentAction.id == id).first()

    if action is None:
        logger.debug(LogMsg.NOT_FOUND)
        raise Http_error(404, Message.NOT_FOUND)

    user = check_user(username, db_session)
    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON)
        raise Http_error(400, Message.INVALID_USER)
    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    if action.person_id != user.person_id:
        logger.error(LogMsg.NOT_ACCESSED, username)
        raise Http_error(403, Message.ACCESS_DENIED)

    try:
        db_session.delete(action)
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(404, Message.NOT_FOUND)

    logger.info(LogMsg.END)
    return Http_response(204, True)


def get_comment_like_count(comment_id, db_session):
    logger.info(LogMsg.START)
    likes = 0
    logger.debug(LogMsg.ACTION_CHECK_COMMENT, comment_id)
    comment = get_comment(comment_id, db_session)
    if comment is None:
        logger.error(LogMsg.NOT_FOUND)
        raise Http_error(404, Message.NOT_FOUND)

    try:
        logger.debug(LogMsg.ACTION_GETTING_LIKES, comment_id)
        likes = db_session.query(CommentAction).filter(
            and_(CommentAction.comment_id == comment_id,
                 CommentAction.like == True)).count()
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(400, Message.NOT_FOUND)
    logger.debug(LogMsg.GET_SUCCESS, {'comment_id': comment_id, 'likes': likes})
    logger.info(LogMsg.END)
    return likes


def get_comment_reports(comment_id, db_session):
    logger.info(LogMsg.START)
    result = []
    logger.debug(LogMsg.ACTION_CHECK_COMMENT, comment_id)
    comment = get_comment(comment_id, db_session)
    if comment is None:
        logger.error(LogMsg.NOT_FOUND)
        raise Http_error(404, Message.NOT_FOUND)

    try:
        logger.debug(LogMsg.ACTION_GETTING_REPORTS, comment_id)
        reports = db_session.query(CommentAction).filter(
            and_(CommentAction.comment_id == comment_id,
                 CommentAction.report != None)).all()
        for item in reports:
            result.append(model_to_dict(item))
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(404, Message.NOT_FOUND)
    logger.debug(LogMsg.GET_SUCCESS, result)
    logger.info(LogMsg.END)
    return result


def get_action_report(comment_id, person_id, db_session):
    logger.info(LogMsg.START)
    return db_session.query(CommentAction).filter(
        and_(CommentAction.comment_id == comment_id,
             CommentAction.person_id == person_id,
             CommentAction.report != None)).first()


def get_action_like(comment_id, person_id, db_session):
    logger.info(LogMsg.START)

    return db_session.query(CommentAction).filter(
        and_(CommentAction.comment_id == comment_id,
             CommentAction.person_id == person_id,
             CommentAction.like == True)).first()


def liked_by_user(db_session, comment_id, username):
    logger.info(LogMsg.START)

    user = check_user(username, db_session)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON)
        raise Http_error(400, Message.Invalid_persons)

    like = get_action_like(comment_id, user.person_id, db_session)
    return True if like is not None else False


def reported_by_user(db_session, comment_id, username):
    logger.info(LogMsg.START)

    user = check_user(username, db_session)
    if user is None:
        if user is None:
            logger.error(LogMsg.INVALID_USER,username)
            raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(400, Message.Invalid_persons)
    report = get_action_report(comment_id, user.person_id, db_session)
    return True if report is not None else False
