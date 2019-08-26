from uuid import uuid4

from sqlalchemy import and_

from book_collections.models import Collection
from helper import Http_error, Now, Http_response
from log import LogMsg,logger
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user
from books.controllers.book import get as get_book


def add(data, db_session, username):
    logger.info(LogMsg.START,username)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(404, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    
    logger.debug(LogMsg.COLLECTION_ADD_NEW_COLLECTION,{'title':data.get('title')})
    book_ids = data.get('books')
    for item in book_ids:
        book = get_book(item, db_session)
        if book is None:
            raise Http_error(404, Message.MSG20)

        collection_item = get(item, user.person_id, data.get('title'),
                              db_session)
        if collection_item is not None:
            raise Http_error(409, Message.ALREADY_EXISTS)

        model_instance = Collection()
        model_instance.id = str(uuid4())
        model_instance.creation_date = Now()
        model_instance.creator = username
        model_instance.version = 1
        model_instance.tags = data.get('tags')

        model_instance.person_id = user.person_id
        model_instance.book_id = item
        model_instance.title = data.get('title')

        db_session.add(model_instance)

    return data


def get_all_collections(db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    collection_items = db_session.query(Collection).filter(
        Collection.person_id == user.person_id).all()
    collections = arrange_collections(collection_items)

    result = []

    for title, colls in collections.items():
        books = []
        for item in colls:
            book = get_book(item, db_session)
            books.append(book)
        result.append({'title': title, 'books': books})

    return result


def get_collection(title,db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    collection_items = db_session.query(Collection).filter(and_(
        Collection.person_id == user.person_id,Collection.title==title)).all()

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
        raise Http_error(502, Message.MSG13)

    return Http_response(204, True)


def delete_books_from_collection(data, db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    book_ids = data.get('books')

    try:
        for id in book_ids:
            db_session.query(Collection).filter(
                and_(Collection.person_id == user.person_id,
                     Collection.book_id == id,
                     Collection.title == data.get('title'))).delete()
    except:
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

    return result
