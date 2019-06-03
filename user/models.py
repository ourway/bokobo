from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from db_session import PrimaryModel, Base


class User(PrimaryModel,Base):
    __tablename__ = 'users'
    username = Column(String, nullable=False, primary_key=True)
    password = Column(String,nullable=False)
    email = Column(String, nullable=False)
    name = Column(String)
    last_name = Column(String)
    addresses = Column(ARRAY(String))
    phones = Column(ARRAY(String))
    image = Column(UUID)
    library = Column(ARRAY(String))