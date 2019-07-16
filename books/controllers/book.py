import json
import logging
from uuid import uuid4

from db_session import client
from elastic.book_index import index_book, delete_book_index, search_phrase, wildcard_es
from file_handler.handle_file import delete_files
from helper import Now, Http_error
from log import LogMsg
from books.models import Book
from enums import BookTypes as legal_types, check_enums, Genre, str_genre, str_type
from messages import Message
from .book_roles import add_book_roles, get_book_roles, book_role_to_dict, delete_book_roles, append_book_roles_dict, \
    books_by_person


def add(db_session, data, username, **kwargs):
    genre = data.get('genre', [])
    if genre and len(genre) > 0:
        check_enums(genre, Genre)

    model_instance = Book()
    model_instance.id = str(uuid4())
    model_instance.title = data.get('title')
    model_instance.edition = data.get('edition')
    model_instance.pub_year = data.get('pub_year')
    model_instance.type = data.get('type')
    model_instance.genre = genre
    model_instance.images = data.get('images')
    model_instance.files = data.get('files')
    model_instance.language = data.get('language')
    model_instance.rate = data.get('rate')
    model_instance.description = data.get('description')
    model_instance.pages = data.get('pages')
    model_instance.duration = data.get('duration')
    model_instance.size = data.get('size')
    model_instance.isben = data.get('isben')
    model_instance.tags = data.get('tags')
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    model_instance.description = data.get('description')

    db_session.add(model_instance)

    # logger.debug(LogMsg.DB_ADD,extra = {'person':model_to_dict(model_instance)})

    # logger.info(LogMsg.END)
    return model_instance


def get(id, db_session):
    logging.info(LogMsg.START)
    logging.debug(LogMsg.MODEL_GETTING)

    model_instance = db_session.query(Book).filter(Book.id == id).first()
    if model_instance:

        logging.debug(LogMsg.GET_SUCCESS +
                      json.dumps(book_to_dict(db_session, model_instance)))

        book_dict = book_to_dict(db_session, model_instance)

    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)

    logging.error(LogMsg.GET_FAILED + json.dumps(book_dict))

    logging.info(LogMsg.END)

    return book_dict


def edit(db_session, data, username):
    logging.info(LogMsg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
        logging.debug(LogMsg.EDIT_REQUST)

    model_instance = db_session.query(Book).filter(Book.id == id).first()
    if model_instance:
        logging.debug(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)

    files = data.get('files', None)
    images = data.get('images', None)
    if files:
        delete_files(model_instance.files)

    if images:
        delete_files(model_instance.images)

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    model_instance.modification_date = Now()
    model_instance.modifier = username

    logging.debug(LogMsg.MODEL_ALTERED)

    logging.debug(LogMsg.EDIT_SUCCESS +
                  json.dumps(book_to_dict(db_session, model_instance)))

    logging.info(LogMsg.END)

    return book_to_dict(db_session, model_instance)


def delete(id, db_session, username):
    logging.info(LogMsg.START + "user is {}  ".format(username) + "book_id = {}".format(id))

    logging.info(LogMsg.DELETE_REQUEST + "user is {}".format(username))

    try:
        book = db_session.query(Book).filter(Book.id == id).first()
        if book.images:
            delete_files(book.images)
        if book.files:
            delete_files(book.files)
        db_session.query(Book).filter(Book.id == id).delete()
        client.delete_object(book)
        logging.debug(LogMsg.ENTITY_DELETED + "Book.id {}".format(id))

    except:
        logging.error(LogMsg.DELETE_FAILED)
        raise Http_error(500, Message.MSG13)

    logging.info(LogMsg.END)
    return {}


def get_all(db_session):
    logging.info(LogMsg.START)
    try:
        final_res = []
        result = db_session.query(Book).all()
        logging.debug(LogMsg.GET_SUCCESS)

        for item in result:
            book_roles = []
            roles = get_book_roles(item.id, db_session)
            for role in roles:
                book_roles.append(book_role_to_dict(role))

            book_dict = book_to_dict(db_session, item)
            book_dict['roles'] = book_roles
            final_res.append(book_dict)
    except:
        logging.error(LogMsg.GET_FAILED)
        raise Http_error(500, Message.MSG14)

    logging.debug(LogMsg.END)
    return final_res


def book_to_dict(db_session, book):
    if not isinstance(book, Book):
        raise Http_error(500, LogMsg.NOT_RIGTH_ENTITY_PASSED.format('Book'))

    result = {
        'creation_date': book.creation_date,
        'creator': book.creator,
        'edition': book.edition,
        'genre': str_genre(book.genre),
        'id': book.id,
        'images': book.images,
        'language': book.language,
        'modification_date': book.modification_date,
        'modifier': book.modifier,
        'pub_year': book.pub_year,
        'rate': book.rate,
        'tags': book.tags,
        'title': book.title,
        'type': book.type.name,
        'version': book.version,
        'roles': append_book_roles_dict(book.id, db_session),
        'files': book.files,
        'description': book.description,
        'pages': book.pages,
        'duration': book.duration,
        'size': book.size,
        'isben': book.isben,

    }

    return result


def add_multiple_type_books(db_session, data, username):
    types = data.get('types')
    check_enums(types, legal_types)

    roles = data.get('roles')

    book_data = {k: v for k, v in data.items() if k not in ['roles', 'types']}

    result = []
    for type in types:
        book_data.update({'type': type})
        book = add(db_session, book_data, username)
        roles, elastic_data = add_book_roles(book.id, roles, db_session, username)

        result.append(book_to_dict(db_session, book))

        index_data = data
        index_data['type'] = type
        index_data['book_id'] = book.id
        index_data['tags'] = book.tags

        del index_data['roles']
        index_data.update(elastic_data)
        index_book(index_data, db_session)

    return result


def edit_book(id, db_session, data, username):
    logging.info(LogMsg.START + " user is {}".format(username))

    model_instance = db_session.query(Book).filter(Book.id == id).first()

    if "id" in data.keys():
        del data["id"]
    logging.debug(LogMsg.EDIT_REQUST)

    if model_instance:
        logging.debug(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.MSG20)

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    model_instance.modification_date = Now()
    model_instance.modifier = username
    model_instance.version += 1

    delete_book_roles(model_instance.id, db_session)
    roles, elastic_data = add_book_roles(model_instance.id, data.get('roles'), db_session, username)
    new_roles = []
    for role in roles:
        new_roles.append(book_role_to_dict(role))

    indexing_data = data
    indexing_data.update(elastic_data)
    indexing_data['book_id'] = model_instance.id
    indexing_data['type'] = model_instance.type
    indexing_data['tags'] = model_instance.tags

    delete_book_index(model_instance.id)
    index_book(indexing_data, db_session)

    edited_book = book_to_dict(db_session, model_instance)

    logging.debug(LogMsg.MODEL_ALTERED)

    logging.info(LogMsg.END)

    return edited_book


def delete_book(id, db_session, username):
    logging.info(LogMsg.START + "user is {}  ".format(username) + "book_id = {}".format(id))

    logging.info(LogMsg.DELETE_REQUEST + "user is {}".format(username))

    try:
        delete(id, db_session, username)
        delete_book_roles(id, db_session)
        delete_book_index(id)

        logging.debug(LogMsg.ENTITY_DELETED + "Book.id {}".format(id))

    except:
        logging.error(LogMsg.DELETE_FAILED)
        raise Http_error(500, Message.MSG13)

    logging.info(LogMsg.END)
    return {}


def search_by_title(data, db_session):
    logging.info(LogMsg.START)
    logging.debug(LogMsg.MODEL_GETTING)

    search_phrase = data.get('search_phrase')
    offset = data.get('offset')
    limit = data.get('limit')

    try:
        result = []
        books = db_session.query(Book).filter(Book.title.like('%{}%'.format(search_phrase))).slice(offset,
                                                                                                   offset + limit)
        for book in books:
            result.append(book_to_dict(db_session, book))
    except:
        raise Http_error(404, Message.MSG20)

    return result


def search_by_writer(data, db_session):
    logging.info(LogMsg.START)
    logging.debug(LogMsg.MODEL_GETTING)
    result = []

    offset = data.get('offset')
    limit = data.get('limit')
    person_id = data.get('search_phrase')
    book_id = data.get('book_id', None)

    try:

        book_ids = books_by_person(person_id, db_session)
        book_ids = set(book_ids)
        if book_id is not None:
            book_ids.remove(book_id)
        books = db_session.query(Book).filter(Book.id.in_(book_ids)).slice(offset, offset + limit)
        for book in books:
            result.append(book_to_dict(db_session, book))
    except:
        raise Http_error(404, Message.MSG20)

    return result


def search_by_genre(data, db_session):
    logging.info(LogMsg.START)
    logging.debug(LogMsg.MODEL_GETTING)

    search_phrase = data.get('search_phrase')
    offset = data.get('offset')
    limit = data.get('limit')
    result = []
    try:

        books = db_session.query(Book).filter(Book.genre.any(search_phrase)).slice(offset, offset + limit)
        for book in books:
            result.append(book_to_dict(db_session, book))
    except:
        raise Http_error(404, Message.MSG20)
    return result


def search_by_tags(data, db_session):
    logging.info(LogMsg.START)
    logging.debug(LogMsg.MODEL_GETTING)

    search_phrase = data.get('search_phrase')
    offset = data.get('offset')
    limit = data.get('limit')
    result = []
    try:

        books = db_session.query(Book).filter(Book.tags.any(search_phrase)).slice(offset, offset + limit)
        for book in books:
            result.append(book_to_dict(db_session, book))
    except:
        raise Http_error(404, Message.MSG20)
    return result


def search_book(data, db_session):
    offset = data.get('offset', 0)
    limit = data.get('limit', 100)
    filter = data.get('filter', None)
    result = []

    if filter is None:
        raise Http_error(400, Message.FILTER_REQUIRED)

    search_key = next(iter(filter.keys()))
    search_phrase = filter.get(search_key)

    search_data = {'limit': limit, 'offset': offset, 'search_phrase': search_phrase}
    if search_key == 'genre':
        result = search_by_genre(search_data, db_session)
    elif search_key == 'title':
        result = search_by_title(search_data, db_session)
    elif search_key == 'writer':
        book_id = filter.get('book_id', None)
        search_data['book_id'] = book_id
        result = search_by_writer(search_data, db_session)
    elif search_key == 'tag':
        result = search_by_tags(search_data, db_session)

    return result


def book_by_ids(id_list, db_session):
    final_res = []
    try:
        result = db_session.query(Book).filter(Book.id.in_(id_list)).all()
        for item in result:
            final_res.append(book_to_dict(db_session, item))

    except:
        raise Http_error(500, Message.MSG14)

    return final_res


def search_by_phrase(data, db_session):
    search_data = {'from': data.get('offset'), 'size': data.get('limit'),
                   'search_phrase': data.get('filter')['search_phrase']}
    res = search_phrase(search_data)
    print(res)
    result = book_by_ids(res, db_session)
    return result


def newest_books(data, db_session):
    offset = data.get('offset')
    limit = data.get('limit')

    try:
        news = db_session.query(Book).order_by(Book.creation_date.desc()).slice(offset, offset + limit)
        res = []
        for book in news:
            res.append(book_to_dict(db_session, book))
    except:
        raise Http_error(404, Message.MSG20)

    return res


def get_current_book(id, db_session):
    logging.info(LogMsg.START)
    logging.debug(LogMsg.MODEL_GETTING)
    model_instance = db_session.query(Book).filter(Book.id == id).first()
    book_roles = []
    book_dict = None
    if model_instance:

        logging.debug(LogMsg.GET_SUCCESS +
                      json.dumps(book_to_dict(db_session, model_instance)))

        book_dict = book_to_dict(db_session, model_instance)

    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)

    logging.info(LogMsg.END)

    return book_dict
