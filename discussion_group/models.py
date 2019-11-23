from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from db_session import Base, PrimaryModel
from user.models import Person


class DiscussionGroup(Base,PrimaryModel):

    __tablename__ = 'discussion_groups'

    title = Column(String,nullable=False)
    description = Column(String)
    image = Column(UUID)
    status = Column(String)

class DiscussionMember(Base,PrimaryModel):

    __tablename__ = 'discussion_members'

    group_id = Column(UUID,ForeignKey(DiscussionGroup.id),nullable=False)
    person_id = Column(UUID,ForeignKey('persons.id'),nullable=False)
    type = Column(String,default='Normal',nullable=False)
    UniqueConstraint(group_id,person_id)


    group = relationship(DiscussionGroup, primaryjoin=group_id == DiscussionGroup.id)
    # person = relationship(Person, primaryjoin=person_id == Person.id)
