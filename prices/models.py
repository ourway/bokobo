from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, Float, UniqueConstraint

from books.models import Book
from db_session import Base, PrimaryModel
from user.models import Person


class Price(Base,PrimaryModel):

    __tablename__ = 'prices'

    book_id = Column(UUID, ForeignKey(Book.id),nullable=False,unique=True)
    price = Column(Float, default=0.00,nullable=False)
    # person_id = Column(UUID, ForeignKey(Person.id),nullable=False)
    #
    # UniqueConstraint(book_id,person_id)
    #
