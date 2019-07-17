import logging
from uuid import uuid4

from books.controllers.book import book_to_dict
from books.controllers.book import get as get_book
from comment.models import Comment
from enums import ReportComment, str_report, check_enum
from helper import Now, Http_error, model_to_dict
from log import LogMsg
from messages import Message
from repository.comment_repo import delete_book_comments
from repository.person_repo import validate_person


def add(db_session, data, username):
    logging.info(LogMsg.START)

    report = data.get('report',None)
    if report :
        check_enum(report, ReportComment)

    book_id = data.get('book_id')
    book = get_book(book_id,db_session)
    if book is None:
        raise Http_error(404,Message.MSG20)

    person_id = data.get('person_id')
    validate_person(person_id,db_session)

    model_instance = Comment()
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    model_instance.person_id = person_id
    model_instance.book_id = book_id
    model_instance.body = data.get('body')
    model_instance.tags = data.get('tags')
    model_instance.parent_id = data.get('parent_id')
    model_instance.helpful = data.get('helpful')
    model_instance.report = report

    db_session.add(model_instance)

    return model_instance


def get(id,db_session,**kwargs):

    try:
        result = db_session.query(Comment).filter(Comment.id == id).first()

    except:
        Http_error(404,Message.MSG20)
    return comment_to_dict(result, db_session)

def delete(id,db_session,**kwargs):
    try:
        db_session.query(Comment).filter(Comment.id == id).delete()
    except:
        raise Http_error(404,Message.MSG13)
    return {}



def delete_comments(book_id,db_session,**kwargs):
    delete_book_comments(book_id, db_session)

    return {}

def get_book_comments(book_id,db_session,**kwargs):

    try:
        res = db_session.query(Comment).filter(Comment.book_id == book_id).all()
        result = []
        for item in res:
            result.append(comment_to_dict(item, db_session))
    except:
        raise Http_error(400,Message.MSG20)

    return result


def comment_to_dict(comment,db_session):

    if not isinstance(comment,Comment):
        raise Http_error(404,Message.INVALID_ENTITY)
    result = {
        'creation_date': comment.creation_date,
        'creator': comment.creator,
        'person_id': comment.person_id,
        'body': comment.body,
        'id': comment.id,
        'modification_date': comment.modification_date,
        'modifier': comment.modifier,
        'parent_id': comment.parent_id,
        'helpful': comment.helpful,
        'report': str_report( comment.report),
        'book_id': comment.book_id,
        'version': comment.version,
        'tags':comment.tags,
        'book':book_to_dict(db_session,comment.book),
        'person':model_to_dict(comment.person)
    }
    return result