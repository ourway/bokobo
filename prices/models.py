from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import  Column, ForeignKey, Float

from books.models import Book
from db_session import Base, PrimaryModel

class Price(Base,PrimaryModel):

    __tablename__ = 'prices'

    book_id = Column(UUID, ForeignKey(Book.id),nullable=False,unique=True)
    price = Column(Float, default=0.00,nullable=False)

