from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, Float

from books.models import Book
from db_session import Base, PrimaryModel
from user.models import Person


class Rate(Base,PrimaryModel):

    __tablename__ = 'rates'
    book_id = Column(UUID,ForeignKey(Book.id),nullable=False)
    person_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    rate = Column(Float,default=0.0)
