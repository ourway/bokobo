from sqlalchemy import or_

from helper import Http_error
from messages import Message
from user.models import Person

def validate_person(person_id,db_session):
    return db_session.query(Person).filter(Person.id == person_id).first()

def person_cell_exists(db_session,cell_no):
    return  db_session.query(Person).filter(Person.cell_no == cell_no).first()

def person_mail_exists(db_session,email):
    return db_session.query(Person).filter(Person.email == email).first()



def validate_persons(person_list,db_session):
        result = db_session.query(Person).filter(Person.id.in_(set(person_list))).all()
        if (result is not None) and (len(set(person_list)) == len(result)):
            return result
        else:
            raise Http_error(404,Message.Invalid_persons)


def person_by_name(search_key,db_session):
    result = db_session.query(Person).filter(or_(Person.name.Like(search_key),Person.last_name.Like(search_key)))