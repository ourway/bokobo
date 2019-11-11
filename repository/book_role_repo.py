from books.models import BookRole


def person_has_books(person_id, db_session):
    result = db_session.query(BookRole).filter(
        BookRole.person_id == person_id).first()
    if result is None:
        return False
    return True


def get_book_press(book_id,db_session):
    return db_session.query(BookRole).filter(BookRole.book_id==book_id,BookRole.role=='Press').first()
