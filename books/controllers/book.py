import json
from uuid import uuid4

from repository.price_repo import delete_book_price
from repository.rate_repo import book_average_rate
from repository.comment_repo import delete_book_comments
from elastic.book_index import index_book, delete_book_index, search_phrase
from file_handler.handle_file import delete_files
from helper import Now, Http_error, populate_basic_data, edit_basic_data, \
    Http_response
from books.models import Book
from enums import BookTypes as legal_types, check_enums, Genre, str_genre
from messages import Message
from .book_roles import add_book_roles, get_book_roles, book_role_to_dict, \
    delete_book_roles, append_book_roles_dict, \
    books_by_person, persons_of_book

from prices.controller import add as add_price, get_book_price_internal
from prices.controller import internal_edit as edit_price
from log import LogMsg, logger
from configs import ADMINISTRATORS


def add(db_session, data, username, **kwargs):
    logger.debug(LogMsg.START, username)

    genre = data.get('genre', [])
    if genre and len(genre) > 0:
        check_enums(genre, Genre)
    logger.debug(LogMsg.ENUM_CHECK, {'genre': genre})

    model_instance = Book()

    populate_basic_data(model_instance, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)

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
    model_instance.description = data.get('description')
    model_instance.from_editor = data.get('from_editor')

    db_session.add(model_instance)
    logger.debug(LogMsg.DB_ADD)

    price = data.get('price', None)
    if price:
        add_price({'book_id': model_instance.id, 'price': price}, db_session,
                  username)

    logger.info(LogMsg.END)
    return model_instance


def get(id, db_session):
    logger.info(LogMsg.START, None)
    logger.debug(LogMsg.MODEL_GETTING, id)

    model_instance = db_session.query(Book).filter(Book.id == id).first()
    if model_instance:
        book_dict = book_to_dict(db_session, model_instance)

        logger.debug(LogMsg.GET_SUCCESS, book_dict)

    else:
        logger.error(LogMsg.NOT_FOUND, {'book_id': id})
        raise Http_error(404, Message.MSG20)

    logger.info(LogMsg.END)

    return book_dict


def edit(id, db_session, data, username):
    logger.info(LogMsg.START, username)
    if "id" in data.keys():
        del data["id"]
    logger.debug(LogMsg.EDIT_REQUST)
    logger.debug(LogMsg.MODEL_GETTING, {'book_id': id})
    model_instance = db_session.query(Book).filter(Book.id == id).first()
    if model_instance:
        logger.debug(LogMsg.GET_SUCCESS)
    else:
        logger.debug(LogMsg.NOT_FOUND, {'book_id': id})
        raise Http_error(404, Message.MSG20)

    if model_instance.creator != username or username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED)
        raise Http_error(403, Message.ACCESS_DENIED)

    logger.debug(LogMsg.EDITING_BOOK, id)

    files = data.get('files', None)
    images = data.get('images', None)
    if files:
        logger.debug(LogMsg.DELETE_BOOK_FILES, id)
        delete_files(model_instance.files)

    if images:
        logger.debug(LogMsg.DELETE_BOOK_IMAGES)
        delete_files(model_instance.images)

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    edit_basic_data(model_instance, username, data.get('tags'))

    price = data.get('price', None)
    if price:
        edit_price(model_instance.id, price, db_session)

    logger.debug(LogMsg.MODEL_ALTERED)

    logger.debug(LogMsg.EDIT_SUCCESS, book_to_dict(db_session, model_instance))

    logger.info(LogMsg.END)

    return book_to_dict(db_session, model_instance)


def delete(id, db_session, username):
    logger.info(
        LogMsg.START, username)

    logger.info(LogMsg.DELETING_BOOK, id)

    logger.debug(LogMsg.MODEL_GETTING, id)
    book = db_session.query(Book).filter(Book.id == id).first()

    if book is None:
        logger.error(LogMsg.NOT_FOUND, {'book_id': id})
        raise Http_error(404, Message.MSG20)

    if book.creator != username and username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED)
        raise Http_error(403, Message.ACCESS_DENIED)

    if book.images:
        logger.debug(LogMsg.DELETE_BOOK_IMAGES)
        delete_files(book.images)
    if book.files:
        logger.debug(LogMsg.DELETE_BOOK_FILES)
        delete_files(book.files)

    db_session.query(Book).filter(Book.id == id).delete()
    logger.debug(LogMsg.ENTITY_DELETED, {"Book.id": id})

    logger.info(LogMsg.END)
    return Http_response(204, True)


def get_all(db_session):
    logger.info(LogMsg.START)
    logger.info(LogMsg.GETTING_ALL_BOOKS)
    try:
        final_res = []
        result = db_session.query(Book).order_by(
            Book.creation_date.desc()).all()
        logger.debug(LogMsg.GET_SUCCESS)

        for item in result:
            book_roles = []
            roles = get_book_roles(item.id, db_session)
            logger.debug(LogMsg.ATTACHING_ROLES_TO_BOOKS)
            for role in roles:
                book_roles.append(book_role_to_dict(role))

            book_dict = book_to_dict(db_session, item)
            book_dict['roles'] = book_roles
            final_res.append(book_dict)
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(500, Message.MSG14)

    logger.debug(LogMsg.END)
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
        'tags': book.tags,
        'title': book.title,
        'version': book.version,
        'roles': append_book_roles_dict(book.id, db_session),
        'files': book.files,
        'description': book.description,
        'pages': book.pages,
        'duration': book.duration,
        'size': book.size,
        'isben': book.isben,
        'from_editor': book.from_editor,
        'price': get_book_price_internal(book.id, db_session)

    }
    if isinstance(book.type, str):
        result['type'] = book.type
    else:
        result['type'] = book.type.name

    rate = book_average_rate(book.id, db_session)
    result['rate'] = rate.get('rate_average')
    result['rate_no'] = rate.get('rate_no')

    return result


def add_multiple_type_books(db_session, data, username):
    logger.info(LogMsg.START, username)
    types = data.get('types')
    logger.debug(LogMsg.ENUM_CHECK, {'book_types': types})
    check_enums(types, legal_types)

    roles_data = data.get('roles')

    book_data = {k: v for k, v in data.items() if k not in ['roles', 'types']}

    result = []
    logger.debug(LogMsg.ADDING_MULTIPLE_BOOKS, data)

    for type in types:
        book_data.update({'type': type})

        logger.debug(LogMsg.ADD_BOOK, book_data)
        book = add(db_session, book_data, username)

        logger.debug(LogMsg.ADDING_ROLES_TO_BOOK, roles_data)
        roles, elastic_data = add_book_roles(book.id, roles_data, db_session,
                                             username)

        result.append(book_to_dict(db_session, book))

        index_data = data
        index_data['type'] = type
        index_data['book_id'] = book.id
        index_data['tags'] = book.tags

        if 'roles' in index_data:
            del index_data['roles']
        index_data.update(elastic_data)

        logger.debug(LogMsg.INDEXING_IN_ELASTIC, index_data)
        index_book(index_data, db_session)

    logger.info(LogMsg.END)

    return result


def edit_book(id, db_session, data, username):
    logger.info(LogMsg.START, username)

    logger.info(LogMsg.EDITING_BOOK, id)

    model_instance = db_session.query(Book).filter(Book.id == id).first()
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'book_id': id})
        raise Http_error(404, Message.MSG20)

    if model_instance.creator != username and username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED)
        raise Http_error(403, Message.ACCESS_DENIED)

    logger.debug(LogMsg.GET_SUCCESS, id)

    if "id" in data.keys():
        del data["id"]
    logger.debug(LogMsg.EDIT_REQUST, {'book_id': id})

    roles = []
    elastic_data = {}

    if 'roles' in data.keys():
        roles = data.get('roles')
        del data['roles']

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    edit_basic_data(model_instance, username, data.get('tags'))

    if len(roles) > 0:
        logger.debug(LogMsg.DELETING_BOOK_ROLES, id)
        delete_book_roles(model_instance.id, db_session)
        logger.debug(LogMsg.ADDING_ROLES_TO_BOOK, id)
        roles, elastic_data = add_book_roles(model_instance.id, roles,
                                             db_session, username)
        new_roles = []
        for role in roles:
            logger.debug(LogMsg.ATTACHING_ROLES_TO_BOOKS, id)
            new_roles.append(book_role_to_dict(role))
    else:
        elastic_data = persons_of_book(model_instance.id, db_session)

    indexing_data = book_to_dict(db_session, model_instance)
    indexing_data['book_id'] = model_instance.id
    indexing_data.update(elastic_data)
    del indexing_data['roles']

    print(('indexing_data : {}').format(indexing_data))

    logger.debug(LogMsg.ELASTIC_INDEX_DELETE, id)
    delete_book_index(model_instance.id)

    logger.debug(LogMsg.INDEXING_IN_ELASTIC, indexing_data)
    index_book(indexing_data, db_session)

    edited_book = book_to_dict(db_session, model_instance)

    logger.debug(LogMsg.MODEL_ALTERED)

    logger.info(LogMsg.END)

    return edited_book


def delete_book(id, db_session, username):
    logger.info(
        LogMsg.START, username)

    logger.info(LogMsg.DELETE_REQUEST, {'book_id': id})

    logger.debug(LogMsg.DELETING_BOOK_ROLES, id)
    delete_book_roles(id, db_session)

    logger.debug(LogMsg.DELETING_BOOK_COMMENTS, id)
    delete_book_comments(id, db_session)

    logger.debug(LogMsg.DELETING_BOOK_PRICE, id)
    delete_book_price(id, db_session)

    delete(id, db_session, username)

    logger.debug(LogMsg.ELASTIC_INDEX_DELETE, id)
    delete_book_index(id)

    logger.debug(LogMsg.ENTITY_DELETED, id)

    logger.info(LogMsg.END)
    return Http_response(204, True)


def search_by_title(data, db_session):
    logger.info(LogMsg.START)

    search_phrase = data.get('search_phrase')
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    logger.debug(LogMsg.SEARCH_BOOK_BY_TITLE, search_phrase)

    try:
        result = []
        books = db_session.query(Book).filter(
            Book.title.like('%{}%'.format(search_phrase))).order_by(
            Book.creation_date.desc()).slice(offset,
                                             offset + limit)
        for book in books:
            result.append(book_to_dict(db_session, book))
        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(404, Message.MSG20)

    logger.info(LogMsg.END)

    return result


def search_by_writer(data, db_session):
    logger.info(LogMsg.START)
    result = []

    offset = data.get('offset', 0)
    limit = data.get('limit', 20)
    person_id = data.get('person_id')
    book_id = data.get('book_id', None)

    try:

        book_ids = books_by_person(person_id, db_session)
        book_ids = set(book_ids)
        if book_id is not None and book_id in book_ids:
            book_ids.remove(book_id)
        books = db_session.query(Book).filter(Book.id.in_(book_ids)).order_by(
            Book.creation_date.desc()).slice(offset, offset + limit)
        for book in books:
            result.append(book_to_dict(db_session, book))
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(404, Message.MSG20)

    return result


def search_by_genre(data, db_session):
    logger.info(LogMsg.START)

    search_phrase = data.get('search_phrase')
    offset = data.get('offset')
    limit = data.get('limit')
    logger.debug(LogMsg.SEARCH_BOOK_BY_GENRE, search_phrase)
    result = []
    try:

        books = db_session.query(Book).filter(
            Book.genre.any(search_phrase)).order_by(
            Book.creation_date.desc()).slice(offset, offset + limit)
        for book in books:
            result.append(book_to_dict(db_session, book))

        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(404, Message.MSG20)

    logger.info(LogMsg.END)
    return result


def search_by_tags(data, db_session):
    logger.info(LogMsg.START)
    logger.debug(LogMsg.MODEL_GETTING)

    search_phrase = data.get('search_phrase')
    offset = data.get('offset')
    limit = data.get('limit')

    logger.debug(LogMsg.SEARCH_BOOK_BY_TAGS, search_phrase)
    result = []

    try:

        books = db_session.query(Book).filter(
            Book.tags.any(search_phrase)).order_by(
            Book.creation_date.desc()).slice(offset, offset + limit)
        for book in books:
            result.append(book_to_dict(db_session, book))

        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(404, Message.MSG20)
    logger.info(LogMsg.END)
    return result


def search_book(data, db_session):
    logger.info(LogMsg.START)
    offset = data.get('offset', 0)
    limit = data.get('limit', 100)
    filter = data.get('filter', None)

    logger.debug(LogMsg.SEARCH_BOOKS, filter)
    result = []

    if filter is None:
        return newest_books(data, db_session)

    search_key = next(iter(filter.keys()))
    search_phrase = filter.get(search_key)

    search_data = {'limit': limit, 'offset': offset,
                   'search_phrase': search_phrase}
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

    logger.info(LogMsg.END)

    return result


def book_by_ids(id_list, db_session):
    logger.info(LogMsg.START)
    final_res = []
    try:
        logger.debug(LogMsg.GETTING_BOOKS_FROM_LIST, id_list)
        result = db_session.query(Book).filter(Book.id.in_(id_list)).all()

        result = sorted(result, key=lambda o: id_list.index(o.id))

        for item in result:
            final_res.append(book_to_dict(db_session, item))

        logger.debug(LogMsg.GET_SUCCESS)

    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(500, Message.MSG14)

    logger.info(LogMsg.END)

    return final_res


def search_by_phrase(data, db_session):
    logger.info(LogMsg.START)
    search_data = {'from': data.get('offset'), 'size': data.get('limit'),
                   'search_phrase': data.get('filter')['search_phrase']}

    logger.debug(LogMsg.SEARCH_ELASTIC_INDEXES, search_data['search_phrase'])
    res = search_phrase(search_data)

    logger.debug(LogMsg.ELASTIC_SEARCH_RESULTS, res)

    result = book_by_ids(res, db_session)
    logger.debug(LogMsg.GETTING_BOOKS_FROM_LIST, res)
    logger.info(LogMsg.END)
    return result


def newest_books(data, db_session):
    logger.info(LogMsg.START)
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    try:
        logger.debug(LogMsg.GETTING_NEWEST_BOOKS)
        news = db_session.query(Book).order_by(Book.creation_date.desc()).slice(
            offset, offset + limit)
        res = []
        for book in news:
            res.append(book_to_dict(db_session, book))

        logger.debug(LogMsg.GET_SUCCESS)
    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(404, Message.MSG20)

    logger.debug(LogMsg.RESULT_BOOKS, res)
    logger.info(LogMsg.END)

    return res


def get_current_book(id, db_session):
    logger.info(LogMsg.START)

    logger.debug(LogMsg.MODEL_GETTING, id)
    model_instance = db_session.query(Book).filter(Book.id == id).first()
    book_roles = []
    book_dict = None
    if model_instance:
        book_dict = book_to_dict(db_session, model_instance)

        logger.debug(LogMsg.GET_SUCCESS, book_dict)

    else:
        logger.debug(LogMsg.NOT_FOUND, id)

    logger.info(LogMsg.END)

    return book_dict
