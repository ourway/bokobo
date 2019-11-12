from log import logger, LogMsg
from repository.user_repo import check_user
from user.models import Person


def full_name_settling(db_session,username):
    logger.info(LogMsg.START,username)
    user = check_user(username,db_session)
    persons = db_session.query(Person).filter(Person.full_name==None).all()

    for person in persons:
        person.full_name = '{} {}'.format(person.last_name,person.name)

    return {'result':True}