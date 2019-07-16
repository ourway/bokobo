from contextlib import contextmanager

from bottle import request
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configs import DATABASE_URI

Base = declarative_base()

engine = create_engine(DATABASE_URI)


class PrimaryModel:
    creation_date = Column(Integer, nullable=False)
    modification_date = Column(Integer)
    id = Column(UUID,nullable=False, primary_key=True,unique=True)
    version = Column(Integer, default=1)
    tags = Column(ARRAY(String))
    creator = Column(String)
    modifier = Column(String)

def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
db_session = Session()


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
