import json
import logging
from uuid import uuid4

from books.controllers.book import book_to_dict
from books.controllers.book import get as get_book
from comment.controllers.actions import get_comment_like_count, get_comment_reports, liked_by_user, reported_by_user
from comment.models import Comment
from helper import Now, Http_error, model_to_dict
from log import LogMsg
from messages import Message
from repository.comment_repo import delete_book_comments, get_comment
from repository.person_repo import validate_person
from repository.user_repo import check_user


def add(db_session, data, username):
    logging.info(LogMsg.START)



    book_id = data.get('book_id')
    book = get_book(book_id,db_session)
    if book is None:
        raise Http_error(404,Message.MSG20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400,Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400,Message.Invalid_persons)

    validate_person(user.person_id,db_session)

    parent_id = data.get('parent_id',None)
    if parent_id:
        parent_comment = get_comment(parent_id,db_session)
        if parent_comment is None:
            raise Http_error(404,Message.PARENT_NOT_FOUND)
        if parent_comment.book_id != book_id:
            raise Http_error(400,Message.ACCESS_DENIED)

    model_instance = Comment()
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    model_instance.person_id = user.person_id
    model_instance.book_id = book_id
    model_instance.body = data.get('body')
    model_instance.tags = data.get('tags')
    model_instance.parent_id = data.get('parent_id')

    db_session.add(model_instance)

    return model_instance


def get(id,db_session,username,**kwargs):

    try:
        result = db_session.query(Comment).filter(Comment.id == id).first()

    except:
        Http_error(404,Message.MSG20)
    return comment_to_dict(db_session,result,username)

def delete(id,db_session,username,**kwargs):

    model_instance = db_session.query(Comment).filter(Comment.id == id).first()
    if model_instance:
        logging.debug(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)
    if user.person_id is None:
        raise Http_error(400,Message.Invalid_persons)

    if model_instance.person_id != user.person_id:
        raise Http_error(403, Message.ACCESS_DENIED)

    try:
        db_session.query(Comment).filter(Comment.id == id).delete()
    except:
        raise Http_error(404,Message.MSG13)
    return {}



def delete_comments(book_id,db_session,username,**kwargs):

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)
    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)


    delete_book_comments(book_id, db_session)

    return {}

def get_book_comments(book_id,db_session,username,**kwargs):

    try:
        res = db_session.query(Comment).filter(Comment.book_id == book_id).all()
        result = []
        for item in res:
            result.append(comment_to_dict( db_session, item,username))
    except:
        raise Http_error(400,Message.MSG20)

    return result



def edit(id,data,db_session,username):
    logging.info(LogMsg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
        logging.debug(LogMsg.EDIT_REQUST)

    model_instance = db_session.query(Comment).filter(Comment.id == id).first()
    if model_instance:
        logging.debug(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400,Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400,Message.Invalid_persons)


    if model_instance.person_id != user.person_id :
        raise Http_error(403,Message.ACCESS_DENIED)

    if 'person_id' in data:
        del data['person_id']
    if 'book_id' in data:
        del data['book_id']


    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    model_instance.modification_date = Now()
    model_instance.modifier = username
    model_instance.version +=1

    logging.debug(LogMsg.MODEL_ALTERED)

    logging.debug(LogMsg.EDIT_SUCCESS +
                  json.dumps(comment_to_dict(db_session, model_instance,username)))

    logging.info(LogMsg.END)

    return comment_to_dict(db_session, model_instance,username)


def comment_to_dict(db_session,comment,username):

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
        'book_id': comment.book_id,
        'version': comment.version,
        'tags':comment.tags,
        'book':book_to_dict(db_session,comment.book),
        'person':model_to_dict(comment.person),
        'likes':get_comment_like_count(comment.id, db_session),
        'reports':len(get_comment_reports(comment.id, db_session)),
        'liked_by_user':liked_by_user(db_session,comment.id,username),
        'reported_by_user':reported_by_user(db_session,comment.id,username),
        'parent': return_parent(comment.parent_id,db_session,username)
    }
    return result


def return_parent(id,db_session,username):
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
        'tags':comment.tags,
        'person':model_to_dict(comment.person),
        'likes':get_comment_like_count(comment.id, db_session),
        'reports':len(get_comment_reports(comment.id, db_session)),
        'liked_by_user':liked_by_user(db_session,comment.id,username),
        'reported_by_user':reported_by_user(db_session,comment.id,username)
    }
    return result