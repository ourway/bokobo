import logging

from .models import Price
from helper import Http_error, populate_basic_data, Http_response, \
    model_to_dict, check_schema
from log import LogMsg
from messages import Message
from books.controllers.book import get as get_book


def add(data, db_session, username):
    logging.info(LogMsg.START)

    check_schema(['price','book_id'],data.keys())

    book_id = data.get('book_id')
    get_book(book_id, db_session)
    model_instance = Price()

    populate_basic_data(model_instance, username)
    model_instance.book_id = book_id
    model_instance.price = data.get('price')

    db_session.add(model_instance)

    return model_instance


def get_by_book(book_id, db_session,username=None):
    return db_session.query(Price).filter(Price.book_id == book_id).first()


def get_all(data, db_session, username=None):
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    result = db_session.query(Price).order_by(
        Price.creation_date.desc()).slice(offset, offset + limit)
    res =[]
    for item in result:
        res.append(model_to_dict(item))

    return res


def get_by_id(id, db_session,username=None):
    return db_session.query(Price).filter(Price.id == id).first()


def delete(id, db_session,username=None):
    price = get_by_id(id, db_session)
    if price is None:
        raise Http_error(404,Message.MSG20)
    if price.creator!=username:
        raise Http_error(403,Message.ACCESS_DENIED)

    try:
        db_session.delete(price)
    except:
        raise Http_error(404, Message.MSG13)

    return Http_response(204, True)


def edit(id,data, db_session,username=None):

    check_schema(['price'],data.keys())

    model_instance = get_by_id(id, db_session)

    if model_instance is None:
        raise Http_error(404, Message.MSG20)
    if model_instance.creator != username:
        raise Http_error(403, Message.ACCESS_DENIED)

    try:
        model_instance.price = data.get('price')
    except:
        raise Http_error(404, Message.MSG13)

    return model_instance