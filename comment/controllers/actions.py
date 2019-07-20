import json
import logging
from uuid import uuid4

from sqlalchemy import and_

from repository.comment_repo import get_comment
from comment.models import CommentAction
from enums import ReportComment, check_enum
from helper import Now, Http_error, model_to_dict
from log import LogMsg
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user


def add(db_session, data, username):
    logging.info(LogMsg.START)

    report = data.get('report', None)
    if report:
        check_enum(report, ReportComment)

    comment_id = data.get('comment_id')
    comment = get_comment(comment_id, db_session)
    if comment is None:
        raise Http_error(404, Message.MSG20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    validate_person(user.person_id, db_session)

    model_instance = CommentAction()

    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    model_instance.comment_id = comment_id
    model_instance.person_id = user.person_id
    model_instance.like = data.get('like')
    model_instance.report = report
    model_instance.tags = data.get('tags')

    db_session.add(model_instance)

    return model_instance


def like(db_session, comment_id, username):
    logging.info(LogMsg.START)

    comment = get_comment(comment_id, db_session)
    if comment is None:
        raise Http_error(404, Message.MSG20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)
    if user.person_id is None:
        raise Http_error(400,Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    action = get_action_like(comment_id, user.person_id, db_session)
    if action is not None:
        raise Http_error(409, Message.ALREADY_LIKED)

    model_instance = CommentAction()

    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    model_instance.comment_id = comment_id
    model_instance.person_id = user.person_id
    model_instance.like = True

    db_session.add(model_instance)

    return model_instance


def dislike(db_session, comment_id, username):
    logging.info(LogMsg.START)

    comment = get_comment(comment_id, db_session)
    if comment is None:
        raise Http_error(404, Message.MSG20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400,Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    action = get_action_like(comment_id, user.person_id, db_session)
    if action is None:
        raise Http_error(404, Message.COMMENT_NOT_FOUND)

    if action.person_id != user.person_id:
        raise Http_error(403, Message.ACCESS_DENIED)

    delete(action.id, db_session, username)

    return {}


def report(db_session, comment_id,data, username):
    logging.info(LogMsg.START)

    comment = get_comment(comment_id, db_session)
    if comment is None:
        raise Http_error(404, Message.MSG20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400,Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    action = get_action_report(comment_id, user.person_id, db_session)
    if action is not None:
        raise Http_error(409, Message.ALREADY_REPORTED)

    report = data.get('report', None)
    if report:
        check_enum(report, ReportComment)

    model_instance = CommentAction()

    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    model_instance.comment_id = comment_id
    model_instance.person_id = user.person_id
    model_instance.report = report

    db_session.add(model_instance)

    return model_instance


def dis_report(db_session, comment_id, username):
    logging.info(LogMsg.START)

    comment = get_comment(comment_id, db_session)
    if comment is None:
        raise Http_error(404, Message.MSG20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400,Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    action = get_action_report(comment_id, user.person_id, db_session)
    if action is None:
        raise Http_error(404, Message.REPORT_NOT_FOUND)

    if action.person_id != user.person_id:
        raise Http_error(403, Message.ACCESS_DENIED)

    delete(action.id, db_session, username)

    return {}


def delete(id, db_session, username):
    action = db_session.query(CommentAction).filter(CommentAction.id == id).first()

    if action:
        logging.debug(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)
    validate_person(user.person_id, db_session)

    if action.person_id != user.person_id:
        raise Http_error(403, Message.ACCESS_DENIED)

    try:
        db_session.query(CommentAction).filter(CommentAction.id == id).delete()
    except:
        raise Http_error(404, Message.MSG20)

    return {}


def get_comment_like_count(comment_id, db_session):
    likes = 0
    try:

        likes = db_session.query(CommentAction).filter(
            and_(CommentAction.comment_id == comment_id, CommentAction.like == True)).count()
    except:
        raise Http_error(400, Message.MSG20)

    return  likes


def get_comment_reports(comment_id, db_session):
    result = []
    try:
        reports = db_session.query(CommentAction).filter(
            and_(CommentAction.comment_id == comment_id, CommentAction.report != None)).all()
        for item in reports:
            result.append(model_to_dict(item))
    except:
        raise Http_error(404, Message.MSG20)

    return result


def get_action_report(comment_id, person_id, db_session):
    return db_session.query(CommentAction).filter(
        and_(CommentAction.comment_id == comment_id, CommentAction.person_id == person_id,
             CommentAction.report != None)).first()


def get_action_like(comment_id, person_id, db_session):
    return db_session.query(CommentAction).filter(
        and_(CommentAction.comment_id == comment_id, CommentAction.person_id == person_id,
             CommentAction.like ==True)).first()

def liked_by_user(db_session,comment_id,username):
    user = check_user(username,db_session)
    if user is None:
        if user is None:
            raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    like = get_action_like(comment_id, user.person_id, db_session)
    return True if like is not None else False


def reported_by_user(db_session, comment_id, username):
    user = check_user(username, db_session)
    if user is None:
        if user is None:
            raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    report = get_action_report(comment_id, user.person_id, db_session)
    return True if report is not None else False

