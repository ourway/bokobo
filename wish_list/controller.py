from sqlalchemy import and_

from helper import Http_error, Now, Http_response, populate_basic_data
from log import LogMsg,logger
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user
from books.controllers.book import get as get_book, book_to_dict
from wish_list.models import WishList


def add(data, db_session, username):
    logger.info(LogMsg.START,username)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS,username)
    book_ids = data.get('books')
    for item in book_ids:
        logger.debug(LogMsg.BOOK_CHECKING_IF_EXISTS,{'id':item})
        book = get_book(item, db_session)

        if book is None:
            logger.error(LogMsg.NOT_FOUND,{'book_id':item})
            raise Http_error(400, Message.NOT_FOUND)

        logger.debug(LogMsg.WISH_CHECK_IF_IN_LIST,{'person_id':user.person_id,'book_id':item})
        wish = get(item, user.person_id, db_session)
        if wish is not None:
            logger.error(LogMsg.WISH_ALREADY_EXISTS,{'person_id':user.person_id,'book_id':item})
            raise Http_error(409, Message.ALREADY_EXISTS)

        model_instance = WishList()
        populate_basic_data(model_instance, username, data.get('tags'))

        model_instance.person_id = user.person_id
        model_instance.book_id = item

        logger.debug(LogMsg.WISH_ADD,{'person_id':user.person_id,'book_id':item})

        db_session.add(model_instance)
        logger.info(LogMsg.END)

    return data


def get_wish_list(data, db_session, username):
    logger.info(LogMsg.START)
    offset = data.get('offset', 0)
    limit = data.get('limit', 10)
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS,username)
    result = []

    book_ids = db_session.query(WishList).filter(
        WishList.person_id == user.person_id).slice(offset, offset + limit)
    for item in book_ids:
        logger.debug(LogMsg.BOOK_CHECKING_IF_EXISTS,item)
        book = get_book(item.book_id, db_session)
        result.append(book)
    logger.debug(LogMsg.WISH_GET,result)
    logger.info(LogMsg.END)
    return result


def delete_wish_list(db_session, username):
    logger.info(LogMsg.START,username)
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS,username)

    try:
        logger.debug(LogMsg.WISH_DELETE_ALL,username)
        db_session.query(WishList).filter(
            WishList.person_id == user.person_id).delete()
        logger.debug(LogMsg.DELETE_SUCCESS,{'username':username})
    except:
        logger.exception(LogMsg.DELETE_FAILED,exc_info=True)
        raise Http_error(502, Message.DELETE_FAILED)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def delete_books_from_wish_list(data, db_session, username):
    logger.info(LogMsg.START,username)
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS,username)

    book_ids = data.get('books')
    logger.debug(LogMsg.WISH_DELETE,book_ids)

    try:
        for id in book_ids:
            db_session.query(WishList).filter(
                and_(WishList.person_id == user.person_id,
                     WishList.book_id == id)).delete()
            logger.debug(LogMsg.WISH_DELETE,id)
    except:
        logger.exception(LogMsg.DELETE_FAILED,exc_info=True)
        raise Http_error(502, Message.DELETE_FAILED)
    logger.info(LogMsg.END)
    return Http_response(204, True)


def get(book_id, person_id, db_session):
    logger.info(LogMsg.START)
    return db_session.query(WishList).filter(and_(WishList.book_id == book_id,
                                                  WishList.person_id == person_id)).first()



def internal_wish_list( db_session, person_id):
    logger.info(LogMsg.START,person_id)

    result = []

    book_ids = db_session.query(WishList).filter(
        WishList.person_id == person_id).all()
    for item in book_ids:
        logger.debug(LogMsg.BOOK_CHECKING_IF_EXISTS,item)
        book = get_book(item.book_id, db_session)
        result.append(book)
    logger.debug(LogMsg.WISH_GET,result)
    logger.info(LogMsg.END)
    return result
