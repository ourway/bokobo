import logging

from book_library.models import Library
from books.controllers.book import book_to_dict
from helper import check_schema, populate_basic_data, Http_error, Http_response, \
    model_basic_dict
from log import LogMsg, logger
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user
from repository.book_repo import get as get_book
from enums import BookTypes


def add(data, db_session):
    logging.info(LogMsg.START)

    check_schema(['book_id', 'person_id'], data.keys())

    book = get_book(data.get('book_id'),db_session)
    if book.type not in [BookTypes.Epub,BookTypes.Audio,BookTypes.Pdf]:
        logger.error(LogMsg.LIBRARY_BOOK_TYPE_NOT_ADDABLE,book.type.name)
        return {}

    model_instance = Library()

    populate_basic_data(model_instance)
    model_instance.person_id = data.get('person_id')
    model_instance.book_id = data.get('book_id')
    model_instance.status = {'status': 'buyed', 'reading_started': False,
                             'read_pages': 0, 'read_duration': 0.00}

    db_session.add(model_instance)
    return model_instance


def get_personal_library(db_session, username):
    user = check_user(username, db_session)
    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    result = db_session.query(Library).filter(
        Library.person_id == user.person_id).all()

    return lib_to_dictlist(result, db_session)


def delete(id, db_session, username):
    model_instance = db_session.query(Library).filter(Library.id == id).first()

    if model_instance is None:
        raise Http_error(404, Message.Msg20)
    if model_instance.creator != username:
        raise Http_error(403, Message.ACCESS_DENIED)

    db_session.delete(model_instance)

    return Http_response(204, True)


def get_user_library(person_id, db_session):
    result = db_session.query(Library).filter(
        Library.person_id == person_id).all()
    return lib_to_dictlist(result, db_session)


def add_books_to_library(person_id, book_list, db_session):
    result = []
    for book_id in book_list:
        lib_data = {'person_id': person_id, 'book_id': book_id}

        result.append(add(lib_data, db_session))
    return result


def edit_status(id, data, db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    model_instance = db_session.query(Library).filter(Library.id == id).first()
    if model_instance.person_id != user.person_id:
        raise Http_error(403, Message.ACCESS_DENIED)

    if data.get('reading_started'):
        model_instance.status['reading_started'] = data.get('reading_started')
    if data.get('read_pages'):
        model_instance.status['read_pages'] = data.get('read_pages')
    if data.get('read_duration'):
        model_instance.status['read_duration'] = data.get('read_duration')

    return model_instance


def lib_to_dictlist(library,db_session):
    result = []
    for item in library:
        res = model_basic_dict(item)
        item_dict = {
            'book_id' :item.book_id,
            'person_id': item.person_id,
            'status': item.status,
            'book': book_to_dict(db_session,item.book)
                }
        item_dict.update(res)
        result.append(item_dict)
    return result

