from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Column, ForeignKey, BOOLEAN, Enum
from sqlalchemy.orm import relationship

from books.models import Book
from db_session import Base, PrimaryModel
from enums import ReportComment
from user.models import Person


class Comment(Base,PrimaryModel):
    __tablename__ = 'comments'

    body = Column(String,nullable=False)
    book_id = Column(UUID, ForeignKey('books.id'),nullable=False)
    person_id = Column(UUID, ForeignKey('persons.id'),nullable=False)
    parent_id = Column(UUID)
    helpful = Column(BOOLEAN,default=False)
    report = Column(Enum(ReportComment))

    person = relationship(Person, primaryjoin=person_id == Person.id , lazy=True)
    book = relationship(Book, primaryjoin=book_id == Book.id)

