from sqlalchemy import and_, update

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

from constraint_handler.controllers.collection_constraint import \
    add as add_uniquecode, unique_code_exists
from constraint_handler.controllers.unique_entity_connector import \
    get_by_entity as get_connector, add as add_connector, \
    delete as delete_connector,get as get_connector_by_unique
from constraint_handler.controllers.common_methods import \
    delete as delete_uniquecode


def add(data, db_session, username):
    logger.info(LogMsg.START, username)

    check_schema(['title'], data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)
    title = data.get('title')

    if username in ADMINISTRATORS and 'person_id' in data:
        person_id = data.get('person_id')
    else:
        user = check_user(username, db_session)
        if user is None:
            raise Http_error(404, Message.INVALID_USER)

        if user.person_id is None:
            logger.error(LogMsg.USER_HAS_NO_PERSON, username)
            raise Http_error(404, Message.Invalid_persons)
        person_id = user.person_id

    validate_person(person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    logger.debug(LogMsg.CHECK_UNIQUE_EXISTANCE, data)
    # unique_code = unique_code_exists(data, db_session)
    # if unique_code is None:
    unique_code = add_uniquecode(data, db_session)

    logger.debug(LogMsg.COLLECTION_ADD_NEW_COLLECTION,
                 {'title': title})
    book_ids = data.get('book_ids', None)

    if book_ids is None:
        logger.debug(LogMsg.COLLECTION_ADD_EMPTY_COLLECTION, {'title': title})

        model_instance = Collection()
        logger.debug(LogMsg.POPULATING_BASIC_DATA)
        populate_basic_data(model_instance, username, data.get('tags'))
        model_instance.person_id = person_id
        model_instance.title = title

        db_session.add(model_instance)
        add_connector(model_instance.id, unique_code.UniqueCode, db_session)
        logger.debug(LogMsg.UNIQUE_CONNECTOR_ADDED,
                     {'collection_id': model_instance.id,
                      'unique_constraint': unique_code.UniqueCode})

        logger.debug(LogMsg.DB_ADD)

        return data

    for item in book_ids:
        log_data = {'book_id': item, 'collection': title}
        logger.debug(LogMsg.COLLECTION_ADD_BOOKS_TO_COLLECTION, title)
        data['book_id'] = item

        collection_item = get(item, person_id, title,
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
        model_instance.title = title

        logger.debug(LogMsg.DB_ADD)
        db_session.add(model_instance)
        add_connector(model_instance.id, unique_code.UniqueCode, db_session)
        logger.debug(LogMsg.UNIQUE_CONNECTOR_ADDED,
                     {'collection_id': model_instance.id,
                      'unique_constraint': unique_code.UniqueCode})

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
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    collection_items = db_session.query(Collection).filter(and_(
        Collection.person_id == user.person_id)).order_by(Collection.creation_date.desc()).all()
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
    logger.info(LogMsg.START, username)
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    collection_items = db_session.query(Collection).filter(and_(
        Collection.person_id == user.person_id,
        Collection.title == title)).order_by(Collection.creation_date.desc()).all()

    result = []

    for item in collection_items:
        if item.book_id is None:
            book = {}
        else:
            book = get_book(item.book_id, db_session)
        result.append(book)


    logger.info(LogMsg.END)

    return result


def delete_collection(title, db_session, username):
    logger.info(LogMsg.START, username)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    try:
        logger.debug(LogMsg.COLLECTION_DELETE, title)
        result = delete_collection_constraints(title, user.person_id,
                                               db_session)
        stmt = Collection.__table__.delete().where(Collection.id.in_(result))

        db_session.execute(stmt)

    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(502, Message.DELETE_FAILED)
    logger.info(LogMsg.END)
    return Http_response(204, True)


def delete_books_from_collection(data, db_session, username):
    logger.info(LogMsg.START, username)

    check_schema(['title', 'book_ids'], data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)

        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    book_ids = data.get('book_ids')
    ids = []

    try:
        logger.debug(LogMsg.COLLECTION_DELETE_BOOK,
                     {'title': data.get('title'), 'books': book_ids})

        result = db_session.query(Collection).filter(
            and_(Collection.person_id == user.person_id,
                 Collection.title == data.get('title'),Collection.book_id.in_(book_ids))).all()
        for item in result:
            ids.append(item.id)
            unique_connector = get_connector(item.id, db_session)
            if unique_connector:
                logger.debug(LogMsg.DELETE_UNIQUE_CONSTRAINT)
                delete_connector(item.id, db_session)
                new_connector = get_connector_by_unique(
                    unique_connector.UniqueCode, db_session)
                if new_connector is None:
                    delete_uniquecode(unique_connector.UniqueCode, db_session)

        stmt = Collection.__table__.delete().where(Collection.id.in_(ids))

        db_session.execute(stmt)

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
    logger.info(LogMsg.START, username)
    limit = data.get('limit', 10)
    offset = data.get('offset', 0)
    final_res = []

    result = db_session.query(Collection).order_by(Collection.creation_date.desc()).slice(offset, offset + limit)
    for item in result:
        final_res.append(collection_to_dict(db_session,item))
    logger.info(LogMsg.END)

    return final_res


def delete_by_id(id, db_session, username):
    logger.info(LogMsg.START, username)
    try:
        logger.debug(LogMsg.DELETE_REQUEST, {'collection_id': id})
        db_session.query(Collection).filter(Collection.id == id).delete()
        unique_connector = get_connector(id, db_session)
        if unique_connector:
            logger.debug(LogMsg.DELETE_UNIQUE_CONSTRAINT)
            delete_connector(id, db_session)
            new_connector = get_connector_by_unique(unique_connector.UniqueCode, db_session)
            if new_connector is None:
                delete_uniquecode(unique_connector.UniqueCode, db_session)

    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(500, Message.DELETE_FAILED)
    logger.info(LogMsg.END)

    return Http_response(204, True)


def collection_to_dict(db_session,collection):
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
        book = book_to_dict(db_session,collection.book)
        model_props['book'] = book
        basic_res.update(model_props)
    return basic_res


def collection_exists(title, person_id, db_session):
    res = db_session.query(Collection).filter(Collection.title == title,
                                              Collection.person_id == person_id).first()
    if res is None:
        return False
    return True


def delete_collection_constraints(title, person_id, db_session):
    result = db_session.query(Collection).filter(Collection.title == title,
                                                 Collection.person_id == person_id).all()
    ids = []
    for item in result:
        unique_connector = get_connector(item.id, db_session)
        if unique_connector:
            logger.debug(LogMsg.DELETE_UNIQUE_CONSTRAINT)
            delete_connector(item.id, db_session)
            new_connector = get_connector_by_unique(unique_connector.UniqueCode,
                                                    db_session)
            if new_connector is None:
                delete_uniquecode(unique_connector.UniqueCode, db_session)
            ids.append(item.id)

    return ids


def rename_collection(title, data, db_session, username):
    logger.info(LogMsg.START, username)

    check_schema(['title'],data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)
    person_id = data.get('person_id')
    if person_id is None:
        user = check_user(username, db_session)
        person_id = user.person_id
        if person_id is None:
            logger.error(LogMsg.USER_HAS_NO_PERSON, username)
            raise Http_error(401, Message.INVALID_USER)

    validate_person(person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    new_title = data.get('title')
    # db_session.update(Collection).Where(Collection.title == title,
    #                                     Collection.person_id == person_id).values(
    #     title=new_title)
    result = db_session.query(Collection).filter(Collection.title == title,
                                               Collection.person_id == person_id).all()
    final_res=[]
    for item in result:
        item.title = new_title

        unique_connector = get_connector(item.id, db_session)
        if unique_connector:
            logger.debug(LogMsg.DELETE_UNIQUE_CONSTRAINT)
            delete_uniquecode(unique_connector.UniqueCode, db_session)
            delete_connector(item.id, db_session)
            db_session.flush()
        model_dict = collection_to_dict(db_session,item)
        print(model_dict)

        logger.debug(LogMsg.CHECK_UNIQUE_EXISTANCE, model_dict)
        unique_code= unique_code_exists(model_dict, db_session)
        if unique_code is None:
            unique_code = add_uniquecode(model_dict, db_session)
        add_connector(item.id, unique_code.UniqueCode, db_session)
        logger.debug(LogMsg.UNIQUE_CONNECTOR_ADDED,
                     {'collection_id': item.id,
                      'unique_constraint': unique_code.UniqueCode})
        final_res.append(model_dict)

    return final_res
