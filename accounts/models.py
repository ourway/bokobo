from sqlalchemy.dialects.postgresql import UUID,ENUM
from sqlalchemy import  Column, ForeignKey, Float

from db_session import Base, PrimaryModel
from enums import AccountTypes
from user.models import Person


class Account(Base,PrimaryModel):

    __tablename__ = 'accounts'

    person_id = Column(UUID, ForeignKey(Person.id),nullable=False)
    value = Column(Float, default=0.00)
    type = Column(ENUM(AccountTypes),nullable=False)

