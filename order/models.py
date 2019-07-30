from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy import Column, ForeignKey, Float, String, JSON, Integer

from books.models import Book
from db_session import Base, PrimaryModel
from enums import OrderStatus
from user.models import Person


class Order(Base,PrimaryModel):

    __tablename__ = 'orders'

    person_id = Column(UUID, ForeignKey(Person.id),nullable=False)
    status = Column(ENUM(OrderStatus),nullable=False,default=OrderStatus.Created)
    total_price = Column(Float,default=0.0)
    description = Column(String)
    price_detail = Column(JSON)


class OrderItem(Base,PrimaryModel):
    __tablename__ = 'order_items'

    order_id = Column(UUID, ForeignKey(Order.id),nullable=False)
    book_id = Column(UUID, ForeignKey(Book.id),nullable=False)
    unit_price = Column(Float,default=0.0)
    discount = Column(Float,default=0.0)
    net_price = Column(Float,default=0.0)
    count = Column(Integer,default=0)
    description = Column(String)
    price_detail = Column(JSON)