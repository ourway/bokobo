from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, String, Boolean, Integer

from discussion_group.models import DiscussionGroup
from db_session import Base, PrimaryModel
from user.models import Person


class ChatMessage(Base,PrimaryModel):

    __tablename__ = 'chat_messages'
    sender_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    receptor_id = Column(UUID,ForeignKey(Person.id))
    group_id = Column(UUID,ForeignKey(DiscussionGroup.id))
    body = Column(String)
    parent_id = Column(UUID)


class LastSeen(Base,PrimaryModel):

    __tablename__ = 'last_seens'
    sender_id = Column(UUID,ForeignKey(Person.id),nullable=False)
    receptor_id = Column(UUID,ForeignKey(Person.id))
    group_id = Column(UUID,ForeignKey(DiscussionGroup.id))
    last_seen = Column(Integer)
