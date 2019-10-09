from sqlalchemy.dialects.postgresql import UUID

from db_session import Base, PrimaryModel
from sqlalchemy import Column, String, ForeignKey


class Group(Base,PrimaryModel):

    __tablename__ = 'groups'

    title = Column(String,unique=True,nullable=False)
    person_id = Column(UUID,ForeignKey('persons.id'))

class GroupUser(Base,PrimaryModel):
    __tablename__='group_users'

    group_id = Column(UUID,ForeignKey('groups.id'),nullable=False)
    user_id = Column(UUID,ForeignKey('users.id'),nullable=False)

