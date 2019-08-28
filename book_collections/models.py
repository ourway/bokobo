from sqlalchemy import ForeignKey, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from books.models import Book
from db_session import Base, PrimaryModel
from user.models import Person


class Collection(Base,PrimaryModel):

    __tablename__ = 'collections'

    person_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    book_id = Column(UUID,ForeignKey(Book.id),nullable=True)
    title = Column(String,nullable=False)

    book = relationship(Book, primaryjoin=book_id == Book.id)
