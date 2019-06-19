from user.models import Person

def validate_person(person_id,db_session):
    return db_session.query(Person).filter(Person.id == person_id).first()

def person_cell_exists(db_session,cell_no):
    return  db_session.query(Person).filter(Person.cell_no == cell_no).first()

def person_mail_exists(db_session,email):
    return db_session.query(Person).filter(Person.email == email).first()
