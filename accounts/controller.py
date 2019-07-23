import logging

from sqlalchemy import and_

from accounts.models import Account
from helper import Http_error, populate_basic_data
from log import LogMsg
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user


def add(data, db_session, username):
    logging.info(LogMsg.START)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(404, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    type = data.get('type')
    account = get(user.person_id, type, db_session)
    if account is not None:
        raise Http_error(409, Message.ALREADY_EXISTS)

    model_instance = Account()

    populate_basic_data(model_instance, username, data.get('tags'))
    model_instance.type = type
    model_instance.person_id = user.person_id
    model_instance.value = data.get('value')


def get(person_id, type, db_session):
    return db_session.query(Account).filter(
        and_(Account.person_id == person_id, Account.type == type)).first()



