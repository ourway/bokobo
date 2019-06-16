from sqlalchemy import Column, String

from db_session import Base,PrimaryModel


class ConstraintHandler(Base,PrimaryModel):

    __tablename__ = 'constraints'
    UniqueCode = Column(String,unique=True, nullable=False)