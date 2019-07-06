from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from db_session import PrimaryModel, Base


class Person(PrimaryModel,Base):

    __tablename__ = 'persons'

    name = Column(String,nullable=False)
    last_name = Column(String)
    address = Column(String)
    phone = Column(String)
    image = Column(UUID)
    email = Column(String,unique=True,nullable=True)
    cell_no = Column(String,unique=True)
    current_book = Column(UUID)


class User(PrimaryModel,Base):
    __tablename__ = 'users'
    username = Column(String, nullable=False,unique=True)
    password = Column(String,nullable=False)
    person_id = Column(UUID,ForeignKey('persons.id'))

    person = relationship(Person, primaryjoin=person_id == Person.id , lazy=True)




