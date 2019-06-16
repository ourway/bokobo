from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from db_session import PrimaryModel, Base


class Person(PrimaryModel,Base):

    __tablename__ = 'presons'

    name = Column(String)
    last_name = Column(String)
    addresses = Column(ARRAY(String))
    phones = Column(ARRAY(String))
    image = Column(UUID)
    email = Column(String)
    cell_no = Column(String)



class User(PrimaryModel,Base):
    __tablename__ = 'users'
    username = Column(String, nullable=False,unique=True)
    password = Column(String,nullable=False)
    person_id = Column(UUID,ForeignKey('presons.id'))

    library = relationship('Library', uselist=True, backref='users')
    person = relationship(Person, primaryjoin=person_id == Person.id , lazy='dynamic')




