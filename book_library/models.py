from sqlalchemy import Column, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from books.models import Book
from db_session import Base, PrimaryModel
from user.models import Person


class Library(Base,PrimaryModel):

    __tablename__ = 'library'

    book_id = Column(UUID,ForeignKey(Book.id),nullable=False)
    person_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    status = Column(JSON)
    progress = Column(Float,default=0.00)

    book = relationship(Book, primaryjoin=book_id == Book.id)
    person = relationship(Person, primaryjoin=person_id == Person.id)


