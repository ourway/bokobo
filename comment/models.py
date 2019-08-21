from sqlalchemy.dialects.postgresql import UUID,ENUM
from sqlalchemy import String, Column, ForeignKey, BOOLEAN
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

    person = relationship(Person, primaryjoin=person_id == Person.id , lazy=True)


class CommentAction(Base,PrimaryModel):

    __tablename__ = 'comment_actions'

    comment_id = Column(UUID, ForeignKey(Comment.id),nullable=False)
    person_id = Column(UUID, ForeignKey('persons.id'),nullable=False)
    like = Column(BOOLEAN, default=False)
    report = Column(ENUM(ReportComment))

