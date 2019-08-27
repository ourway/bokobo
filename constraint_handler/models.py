from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from db_session import Base,PrimaryModel

class ConstraintHandler(Base,PrimaryModel):

    __tablename__ = 'constraints'
    UniqueCode = Column(String,unique=True, nullable=False)

class UniqueEntityConnector(Base, PrimaryModel):
    __tablename__ = 'unique_entity_connector'
    UniqueCode = Column(String, unique=True, nullable=False)
    entity_id = Column(UUID,unique=True,nullable=False)
