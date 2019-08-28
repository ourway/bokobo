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
    logger.debug(LogMsg.SCHEMA_CHECKED)

    if username in ADMINISTRATORS and 'person_id' in data:
        person_id = data.get('person_id')
    else:
        user = check_user(username, db_session)
        if user is None:
            raise Http_error(404, Message.INVALID_USER)

        if user.person_id is None:
            logger.error(LogMsg.USER_HAS_NO_PERSON,username)
            raise Http_error(404, Message.Invalid_persons)
        person_id = user.person_id

    validate_person(person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    logger.debug(LogMsg.COLLECTION_ADD_NEW_COLLECTION,
                 {'title': data.get('title')})
    book_ids = data.get('book_ids',None)

    if book_ids is None:
        logger.debug(LogMsg.COLLECTION_ADD_EMPTY_COLLECTION,{'title':data.get('title')})
        model_instance = Collection()
        logger.debug(LogMsg.POPULATING_BASIC_DATA)
        populate_basic_data(model_instance, username, data.get('tags'))
        model_instance.person_id = person_id
        model_instance.title = data.get('title')

        db_session.add(model_instance)
        logger.debug(LogMsg.DB_ADD)

        return data

    for item in book_ids:
        log_data = {'book_id': item, 'collection': data.get('title')}
        logger.debug(LogMsg.COLLECTION_ADD_BOOKS_TO_COLLECTION,
                     data.get('title'))

        collection_item = get(item, person_id, data.get('title'),
                              db_session)
        if collection_item is not None:
            logger.error(LogMsg.COLLECTION_BOOK_ALREADY_EXISTS, log_data)
            raise Http_error(409, Message.ALREADY_EXISTS)

        if not is_book_in_library(person_id, item, db_session):
            logger.error(LogMsg.COLLECTION_BOOK_IS_NOT_IN_LIBRARY,
                         {'book_id': item})
            raise Http_error(403, Message.BOOK_NOT_IN_LIB)

        logger.debug(LogMsg.COLLECTION_CHECK_BOOK_IS_IN_COLLECTION, log_data)


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
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    collection_items = db_session.query(Collection).filter(and_(
        Collection.person_id == user.person_id)).all()
    collections, titles = arrange_collections(collection_items)
    logger.debug(LogMsg.COLLECTION_ARRANGE_BY_TITLE)

    result = []

    for title, colls in collections.items():
        books = []
        for item in colls:
            if item is None:
                pass
            else:
                book = get_book(item, db_session)
                books.append(book)
        result.append({'title': title, 'books': books})
    return result


def get_collection(title, db_session, username):
    logger.info(LogMsg.START,username)
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    collection_items = db_session.query(Collection).filter(and_(
        Collection.person_id == user.person_id, Collection.title == title)).all()

    result = []

    for item in collection_items:
        if item.book_id is None:
            book = {}
        else:
            book = get_book(item.book_id, db_session)
        result.append(book_to_dict(book))

    logger.info(LogMsg.END)

    return result


def delete_collection(title, db_session, username):
    logger.info(LogMsg.START,username)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    try:
        logger.debug(LogMsg.COLLECTION_DELETE,title)
        db_session.query(Collection).filter(
            Collection.person_id == user.person_id,
            Collection.title == title).delete()
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(502, Message.DELETE_FAILED)
    logger.info(LogMsg.END)
    return Http_response(204, True)


def delete_books_from_collection(data, db_session, username):
    logger.info(LogMsg.START,username)

    check_schema(['title', 'book_ids'], data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)

        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    book_ids = data.get('book_ids')

    try:
        logger.debug(LogMsg.COLLECTION_DELETE_BOOK,{'title':data.get('title'),'books':book_ids})
        for id in book_ids:
            db_session.query(Collection).filter(
                and_(Collection.person_id == user.person_id,
                     Collection.book_id == id,
                     Collection.title == data.get('title'))).delete()
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(502, Message.DELETE_FAILED)
    logger.info(LogMsg.END)
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
    logger.info(LogMsg.START,username)
    limit = data.get('limit', 10)
    offset = data.get('offset', 0)
    final_res = []

    result = db_session.query(Collection).slice(offset, offset + limit)
    for item in result:
        final_res.append(collection_to_dict(item))
    logger.info(LogMsg.END)

    return final_res


def delete_by_id(id, db_session, username):
    logger.info(LogMsg.START,username)
    try:
        logger.debug(LogMsg.DELETE_REQUEST,{'collection_id':id})
        db_session.query(Collection).filter(Collection.id == id).delete()
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, Message.DELETE_FAILED)
    logger.info(LogMsg.END)

    return Http_response(204, True)


def collection_to_dict(collection):
    if not isinstance(collection, Collection):
        raise Http_error(400, Message.INVALID_ENTITY)
    basic_res = model_basic_dict(collection)
    model_props = {
        'book_id': collection.book_id,
        'person_id': collection.person_id,
        'title': collection.title,
        'book': None
    }
    if collection.book_id is not None:
        book = book_to_dict(collection.book)
        model_props['book'] = book

    return basic_res.update(model_props)
