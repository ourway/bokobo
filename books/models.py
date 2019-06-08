from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Integer, Column
from db_session import Base, PrimaryModel

class Book(Base,PrimaryModel):
    __tablename__ = 'books'
    title = Column(String,nullable=False)
    authors = Column(ARRAY(String),nullable=False)
    edition = Column(Integer,default=1)
    press = Column(ARRAY(String),nullable=False)
    translator = Column(ARRAY(String))
    editors =Column(ARRAY(String))
    narrators = Column(ARRAY(String))
    pub_year = Column(Integer)
    types = Column(ARRAY(String))
    language = Column(String, default='farsi')


