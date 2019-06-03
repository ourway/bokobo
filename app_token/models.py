from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from db_session import Base


class APP_Token(Base):

    __tablename__ = 'app_tokens'
    id = Column(UUID,primary_key=True,nullable=False)
    username = Column(String, nullable=False)
    expiration_date = Column(Integer, nullable=False)
