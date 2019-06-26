import json
import logging
import os
from uuid import uuid4

from helper import model_to_dict, Now, value, Http_error
from log import logger, LogMsg
from books.models import Book
from enums import BookTypes as legal_types,Roles, check_enums
from .book_roles import add_book_roles

save_path = os.environ.get('save_path')




def add(db_session, data, username):
        # logger.info(LogMsg.START,extra={'data':data,'user':username})


    model_instance = Book()
    model_instance.id = str(uuid4())
    model_instance.title = data.get('title')
    model_instance.edition = data.get('edition')
    model_instance.pub_year = data.get('pub_year')
    model_instance.type = data.get('type')
    model_instance.genre = data.get('genre')
    model_instance.language = data.get('language')
    model_instance.rate = data.get('rate')
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1

    images = data.get('image', [])
    model_images  =[]
    if len(images) > 0:
        for image in images:
            if image:
                image.filename = str(uuid4())
                model_images.append(image.filename)

            image.save(save_path)
        del (data['image'])

        model_instance.images = model_images

# logger.debug(LogMsg.DATA_ADDITION)

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
                      json.dumps(book_to_dict(model_instance)))
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": LogMsg.NOT_FOUND})

    logging.error(LogMsg.GET_FAILED + json.dumps({"id": id}))

    logging.info(LogMsg.END)

    return book_to_dict(model_instance)


def edit(db_session, data, username):
    logging.info(LogMsg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]
        logging.debug(LogMsg.EDIT_REQUST)

    model_instance = get(id, db_session, username)
    if model_instance:
        logging.debug(LogMsg.MODEL_GETTING)
    else:
        logging.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": LogMsg.NOT_FOUND})

    if data.get('tags') is not None:
        tags = (data.get('tags')).split(',')
        for item in tags:
            item.strip()
        model_instance.tags = tags

        del data['tags']

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    model_instance.modification_date = Now()
    model_instance.modifier = username

    logging.debug(LogMsg.MODEL_ALTERED)

    logging.debug(LogMsg.EDIT_SUCCESS +
                  json.dumps(model_to_dict(model_instance)))

    logging.info(LogMsg.END)

    return book_to_dict(model_instance)


def delete(id, db_session, username):
    logging.info(LogMsg.START + "user is {}  ".format(username) + "token_id = {}".format(id))

    logging.info(LogMsg.DELETE_REQUEST + "user is {}".format(username))

    try:
        db_session.query(Book).filter(Book.id == id).delete()

        logging.debug(LogMsg.ENTITY_DELETED + "Book.id {}".format(id))

    except:
        logging.error(LogMsg.DELETE_FAILED)
        raise Http_error(500, LogMsg.DELETE_FAILED)

    logging.info(LogMsg.END)
    return {}


def get_all(db_session):
    logging.info(LogMsg.START )
    try:
        final_res = []
        result = db_session.query(Book).all()
        logging.debug(LogMsg.GET_SUCCESS)
        for item in result:
            final_res.append(book_to_dict(item))
    except:
        logging.error(LogMsg.GET_FAILED)
        raise Http_error(500, LogMsg.GET_FAILED)

    logging.debug(LogMsg.END)
    return final_res

def book_to_dict(book):
    if not isinstance(book, Book):
        raise Http_error(400, LogMsg.NOT_RIGTH_ENTITY_PASSED.format('Book'))

    result = {
        # 'book_roles': model_to_dict(book.book_roles),
        'creation_date': book.creation_date,
        'creator': book.creator,
        'edition': book.edition,
        'genre': model_to_dict(book.genre),
        'id': book.id,
        'images': model_to_dict(book.images),
        'language': book.language,
        # 'library': model_to_dict(book.library),
        'modification_date': book.modification_date,
        'modifier': book.modifier,
        # 'persons': model_to_dict(book.persons),
        'pub_year': book.pub_year,
        'rate': book.rate,
        'tags': book.tags,
        'title': book.title,
        'type': model_to_dict(book.type),
        # 'users': model_to_dict(book.users),
        'version': book.version
    }

    return result



def add_multiple_type_books(db_session, data, username):
    types = data.get('types')
    check_enums(types, legal_types)

    roles = data.get('roles')
    check_enums(roles.keys(), Roles)

    book_data = data.get('book')

    result = []

    for type in types:
        book_data.update({'type': type})
        book = add(db_session, data, username)
        add_book_roles(book.id, roles, db_session, username)

        result.append(book_to_dict(book))

    return result

