from books.models import BookContent


def delete(book_id,db_session):
    db_session.query(BookContent).filter(BookContent.book_id == book_id).delete()
    return True