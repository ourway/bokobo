import logging
from uuid import uuid4

from sqlalchemy import and_

from helper import Http_error, Now, Http_response
from log import LogMsg
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user
from books.controllers.book import get as get_book, book_to_dict
from wish_list.models import WishList


def add(data, db_session, username):
    logging.info(LogMsg.START)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    book_ids = data.get('books')
    for item in book_ids:
        book = get_book(item, db_session)
        if book is None:
            raise Http_error(400, Message.MSG20)

        wish = get(item, user.person_id, db_session)
        if wish is not None:
            raise Http_error(409,Message.ALREADY_EXISTS)

        model_instance = WishList()
        model_instance.id = str(uuid4())
        model_instance.creation_date = Now()
        model_instance.creator = username
        model_instance.version = 1
        model_instance.tags = data.get('tags')

        model_instance.person_id = user.person_id
        model_instance.book_id = item

        db_session.add(model_instance)

    return data


def get_wish_list(db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    result = []

    book_ids = db_session.query(WishList).filter(
        WishList.person_id == user.person_id).all()
    for item in book_ids:
        book = get_book(item.book_id, db_session)
        result.append(book)

    return result


def delete_wish_list(db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    try:
        db_session.query(WishList).filter(WishList.person_id == user.person_id).delete()
    except:
        raise Http_error(502, Message.MSG13)

    return Http_response(204,True)


def delete_books_from_wish_list(data, db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    book_ids = data.get('books')

    try:
        for id in book_ids:
            db_session.query(WishList).filter(and_(WishList.person_id == user.person_id,
                                         WishList.book_id == id)).delete()
    except:
        raise Http_error(502, Message.MSG13)

    return Http_response(204,True)


def get(book_id, person_id, db_session):
    return db_session.query(WishList).filter(and_(WishList.book_id == book_id,
                                                  WishList.person_id == person_id)).first()
