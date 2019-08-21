from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db_session import Base, PrimaryModel
from user.models import Person


class Follow(Base,PrimaryModel):

    __tablename__ = 'follows'

    follower_id = Column(UUID, ForeignKey('persons.id'),nullable=False)
    following_id = Column(UUID, ForeignKey('persons.id'),nullable=False)

    follower = relationship(Person, primaryjoin=follower_id == Person.id , lazy=True)
    following = relationship(Person, primaryjoin=following_id == Person.id , lazy=True)