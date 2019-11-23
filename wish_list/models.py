from sqlalchemy import ForeignKey, Column
from sqlalchemy.dialects.postgresql import UUID

from books.models import Book
from db_session import Base, PrimaryModel
from user.models import Person

class WishList(Base,PrimaryModel):
    __tablename__ = 'wish_lists'

    person_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    book_id = Column(UUID,ForeignKey(Book.id),nullable=False)
