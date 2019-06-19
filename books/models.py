from sqlalchemy.dialects.postgresql import ARRAY,UUID
from sqlalchemy import String, Integer, Column, ForeignKey, Float, Enum, UniqueConstraint
from sqlalchemy.orm import relationship

from db_session import Base, PrimaryModel
from configs import Roles,BookTypes,Genre
from user.models import Person, User


class Book(Base,PrimaryModel):
    __tablename__ = 'books'
    title = Column(String,nullable=False)
    edition = Column(String,default=1)
    pub_year = Column(Integer)
    type = Column(Enum(BookTypes))
    genre = Column(Enum(Genre))
    language = Column(String)
    rate = Column(Float)

    persons = relationship('BookRole', uselist=True, backref='books')
    users = relationship('Library', uselist=True, backref='books')



class BookRole(Base,PrimaryModel):
    __tablename__ = 'book_roles'

    book_id = Column(UUID,ForeignKey('books.id'),nullable=False)
    person_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    role = Column(Enum(Roles),nullable=False)

    book = relationship(Book, primaryjoin=book_id == Book.id , lazy='dynamic', backref='book_roles')
    person = relationship(Person, primaryjoin=person_id == Person.id , lazy='dynamic')


class Library(Base,PrimaryModel):

    __tablename__ = 'library'

    book_id = Column(UUID,ForeignKey('books.id'),nullable=False)
    user_id = Column(UUID,ForeignKey(User.id),nullable=False)

    book = relationship(Book, primaryjoin=book_id == Book.id, lazy='dynamic',backref='library')
    user = relationship(User, primaryjoin=user_id == User.id, lazy='dynamic',backref = 'library')


