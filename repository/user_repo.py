from sqlalchemy import and_,or_

from user.models import User, Person


def check_user(username, db_session):
    return db_session.query(User).filter(User.username == username).first()

def check_by_cell_no(cell_no,db_session):
    user = db_session.query(User).filter(User.username == cell_no).first()
    if not user:
        person = db_session.query(Person).filter(Person.cell_no == cell_no).first()
        if person:
            user = db_session.query(User).filter(User.person_id == person.id).first()

    return user

def check_by_username(username,db_session):
    user = db_session.query(User).filter(User.username == username).first()

    return user

def check_by_id(id,db_session):
    user = db_session.query(User).filter(User.id == id).first()

    return user