from books.models import BookRole


def person_has_books(person_id, db_session):
    result = db_session.query(BookRole).filter(
        BookRole.person_id == person_id).first()
    if result is None:
        return False
    return True
