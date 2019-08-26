from uuid import uuid4

from sqlalchemy import and_

from book_collections.models import Collection
from book_library.controller import is_book_in_library
from helper import Http_error, populate_basic_data, Http_response, check_schema, \
    model_basic_dict
from log import LogMsg, logger
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user
from books.controllers.book import get as get_book, book_to_dict
from configs import ADMINISTRATORS


def add(data, db_session, username):
    logger.info(LogMsg.START, username)

    check_schema(['title'], data.keys())

    if username in ADMINISTRATORS and 'person_id' in data:
        person_id = data.get('person_id')
    else:
        user = check_user(username, db_session)
        if user is None:
            raise Http_error(404, Message.INVALID_USER)

        if user.person_id is None:
            raise Http_error(404, Message.Invalid_persons)
        person_id = user.person_id

    validate_person(person_id, db_session)

    logger.debug(LogMsg.COLLECTION_ADD_NEW_COLLECTION,
                 {'title': data.get('title')})
    book_ids = data.get('book_ids',None)

    if book_ids is None:
        model_instance = Collection()
        logger.debug(LogMsg.POPULATING_BASIC_DATA)
        populate_basic_data(model_instance, username, data.get('tags'))
        model_instance.person_id = person_id
        model_instance.title = data.get('title')

        logger.debug(LogMsg.DB_ADD)
        db_session.add(model_instance)
        return data

    for item in book_ids:
        log_data = {'book_id': item, 'collection': data.get('title')}
        logger.debug(LogMsg.COLLECTION_ADD_BOOKS_TO_COLLECTION,
                     data.get('title'))

        if not is_book_in_library(person_id, item, db_session):
            logger.error(LogMsg.COLLECTION_BOOK_IS_NOT_IN_LIBRARY,
                         {'book_id': item})
            raise Http_error(403, Message.BOOK_NOT_IN_LIB)

        logger.debug(LogMsg.COLLECTION_CHECK_BOOK_IS_IN_COLLECTION, log_data)

        collection_item = get(item, person_id, data.get('title'),
                              db_session)
        if collection_item is not None:
            logger.error(LogMsg.COLLECTION_BOOK_ALREADY_EXISTS, log_data)
            raise Http_error(409, Message.ALREADY_EXISTS)

        model_instance = Collection()
        logger.debug(LogMsg.POPULATING_BASIC_DATA)
        populate_basic_data(model_instance, username, data.get('tags'))
        model_instance.person_id = person_id
        model_instance.book_id = item
        model_instance.title = data.get('title')

        logger.debug(LogMsg.DB_ADD)
        db_session.add(model_instance)

        logger.info(LogMsg.END)

    return data


def add_book_to_collections(data, db_session, username):
    logger.info(LogMsg.START, username)

    check_schema(['book_id', 'collections'], data.keys())
    logger.debug(LogMsg.COLLECTION_ADD_BOOK_TO_MULTIPLE_COLLECTIONS, data)
    book_id = data.get('book_id')
    for collection_title in data.get('collections'):
        addition_data = {'book_ids': [book_id], 'title': collection_title}
        add(addition_data, db_session, username)
    logger.info(LogMsg.END)

    return data


def get_all_collections(db_session, username):
    logger.info(LogMsg.START, username)
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    collection_items = db_session.query(Collection).filter(and_(
        Collection.person_id == user.person_id,
        Collection.book_id != None)).all()
    collections, titles = arrange_collections(collection_items)

    result = []

    for title, colls in collections.items():
        books = []
        for item in colls:
            book = get_book(item, db_session)
            books.append(book)
        result.append({'title': title, 'books': books})

    return result


def get_collection(title, db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    collection_items = db_session.query(Collection).filter(and_(
        Collection.person_id == user.person_id, Collection.title == title,
        Collection.book_id != None)).all()

    result = []

    for item in collection_items:
        book = get_book(item.book_id, db_session)
        result.append(book)

    return result


def delete_collection(title, db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    try:
        db_session.query(Collection).filter(
            Collection.person_id == user.person_id,
            Collection.title == title).delete()
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(502, Message.MSG13)

    return Http_response(204, True)


def delete_books_from_collection(data, db_session, username):
    check_schema(['title', 'book_ids'], data.keys())
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    book_ids = data.get('book_ids')

    try:
        for id in book_ids:
            db_session.query(Collection).filter(
                and_(Collection.person_id == user.person_id,
                     Collection.book_id == id,
                     Collection.title == data.get('title'))).delete()
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(502, Message.MSG13)

    return Http_response(204, True)


def get(book_id, person_id, title, db_session):
    return db_session.query(Collection).filter(
        and_(Collection.book_id == book_id,
             Collection.person_id == person_id,
             Collection.title == title)).first()


def arrange_collections(collection_items):
    titles = set()
    result = {}

    for item in collection_items:
        titles.add(item.title)
        if result.get(item.title) is None:
            result[item.title] = [item.book_id]
        else:
            (result[item.title]).append(item.book_id)

    return result, titles


def get_all(data, db_session, username):
    limit = data.get('limit', 10)
    offset = data.get('offset', 0)
    final_res = []

    result = db_session.query(Collection).filter(
        Collection.book_id != None).slice(offset, offset + limit)
    for item in result:
        final_res.append(collection_to_dict(item))
    return final_res


def delete_by_id(id, db_session, username):
    try:
        db_session.query(Collection).filter(Collection.id == id).delete()
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, Message.MSG13)
    return Http_response(204, True)


def collection_to_dict(collection):
    if not isinstance(collection, Collection):
        raise Http_error(400, Message.INVALID_ENTITY)
    basic_res = model_basic_dict(collection)
    model_props = {
        'book_id': collection.book_id,
        'person_id': collection.person_id,
        'title': collection.title,
        'book': book_to_dict(collection.book)
    }
    return basic_res.update(model_props)
