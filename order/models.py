from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Integer, Column
from db_session import Base, PrimaryModel


class Order(Base,PrimaryModel):

    __tablename__ = 'orders'

    title = Column(String)
    owner = Column(String)
    status = Column(String)
    items = Column(ARRAY(String))