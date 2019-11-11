from books.models import Book
from log import logger, LogMsg
from repository.book_role_repo import get_book_press
from repository.user_repo import check_user


def book_press_settling(db_session,username):
    logger.info(LogMsg.START,username)
    user = check_user(username,db_session)
    books = db_session.query(Book).filter(Book.press==None).all()

    for book in books:
        press = get_book_press(book.id, db_session)
        if press is None:
            logger.error(LogMsg.DATA_MISSING,{'book_id':book.id,'missing':'press_role'})
            # book.press = user.person_id

        else:
            book.press=press.person_id
    return {'result':True}