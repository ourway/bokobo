from books.models import Book

def get(id, db_session):

    model_instance = db_session.query(Book).filter(Book.id == id).first()
    return model_instance