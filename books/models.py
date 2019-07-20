from sqlalchemy.dialects.postgresql import ARRAY,UUID
from sqlalchemy import String, JSON, Column, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from db_session import Base, PrimaryModel
from enums import Roles,BookTypes
from user.models import Person, User


class Book(Base,PrimaryModel):
    __tablename__ = 'books'
    title = Column(String,nullable=False)
    edition = Column(String,default='1')
    pub_year = Column(String)
    type = Column(Enum(BookTypes))
    genre = Column(ARRAY(String))
    language = Column(String)
    rate = Column(Float)
    images = Column(ARRAY(UUID))
    files = Column(ARRAY(UUID))
    description = Column(String)
    pages = Column(String)
    duration = Column(String)
    size = Column(String)
    isben = Column(String)
    from_editor = Column(String)


class BookRole(Base,PrimaryModel):
    __tablename__ = 'book_roles'

    book_id = Column(UUID,ForeignKey(Book.id),nullable=False)
    person_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    role = Column(Enum(Roles),nullable=False)

    book_roles = relationship(Book, primaryjoin=book_id == Book.id )
    person = relationship(Person, primaryjoin=person_id == Person.id )


class Library(Base,PrimaryModel):

    __tablename__ = 'library'

    book_id = Column(UUID,ForeignKey(Book.id),nullable=False)
    user_id = Column(UUID,ForeignKey(User.id),nullable=False)
    status = Column(JSON)

    book = relationship(Book, primaryjoin=book_id == Book.id)
    user = relationship(User, primaryjoin=user_id == User.id,backref = 'library')


