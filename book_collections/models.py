from sqlalchemy import ForeignKey, Column, String,ARRAY
from sqlalchemy.dialects.postgresql import UUID

from books.models import Book
from db_session import Base, PrimaryModel
from user.models import Person


class Collection(Base,PrimaryModel):

    __tablename__ = 'collections'

    person_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    book_id = Column(ARRAY(UUID),ForeignKey(Book.id),nullable=False)
    title = Column(String,nullable=False)
