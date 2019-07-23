from sqlalchemy import Column, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from books.models import Book
from db_session import Base, PrimaryModel
from user.models import User


class Library(Base,PrimaryModel):

    __tablename__ = 'library'

    book_id = Column(UUID,ForeignKey(Book.id),nullable=False)
    user_id = Column(UUID,ForeignKey(User.id),nullable=False)
    status = Column(JSON)

    book = relationship(Book, primaryjoin=book_id == Book.id)
    user = relationship(User, primaryjoin=user_id == User.id,backref = 'library')


