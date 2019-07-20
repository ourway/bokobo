import logging
from uuid import uuid4

from sqlalchemy import and_

from book_rate.models import Rate
from books.controllers.book import get as get_book
from helper import Http_error, Now
from log import LogMsg
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user


def add(db_session, data, username):
    logging.info(LogMsg.START)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    book = get_book(data.get('book_id'), db_session)
    if book is None:
        raise Http_error(400, Message.MSG20)

    rate = get(data.get('book_id'), user.person_id, db_session)
    if rate:
        rate.rate = data.get('rate')
        return rate

    else:

        model_instance = Rate()
        model_instance.id = str(uuid4())
        model_instance.creation_date = Now()
        model_instance.creator = username
        model_instance.version = 1
        model_instance.tags = data.get('tags')

        model_instance.person_id = user.person_id
        model_instance.rate = data.get('rate')
        model_instance.book_id = data.get('book_id')

        db_session.add(model_instance)

        return model_instance


def get(book_id, person_id, db_session):
    return db_session.query(Rate).filter(and_(Rate.book_id == book_id, Rate.person_id == person_id)).first()



def edit(id, data, db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    model_instance = db_session.query(Rate).filter(Rate.id == id).first()

    if model_instance:
        logging.debug(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)

    if model_instance.person_id != user.person_id:
        raise Http_error(403, Message.ACCESS_DENIED)

    model_instance.rate = data.get('rate')
    model_instance.modification_date = Now()
    model_instance.modifier = username
    model_instance.version += 1

    logging.debug(LogMsg.MODEL_ALTERED)

    return model_instance


def delete(id, db_session, username, **kwargs):
    model_instance = db_session.query(Rate).filter(Rate.id == id).first()
    if model_instance:
        logging.debug(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)
    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    if model_instance.person_id != user.person_id:
        raise Http_error(403, Message.ACCESS_DENIED)

    try:
        db_session.query(Rate).filter(Rate.id == id).delete()
    except:
        raise Http_error(404, Message.MSG13)
    return {}
