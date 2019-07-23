import logging

from sqlalchemy import and_

from accounts.models import Account
from enums import check_enum, AccountTypes, str_account_type
from helper import Http_error, populate_basic_data, model_to_dict, \
    Http_response, model_basic_dict
from log import LogMsg
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user


def add(data, db_session, username):
    logging.info(LogMsg.START)

    check_enum(data.get('type'),AccountTypes)

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

    db_session.add(model_instance)

    return account_to_dict(model_instance)


def get(person_id, type, db_session):
    return db_session.query(Account).filter(
        and_(Account.person_id == person_id, Account.type == type)).first()


def get_all(data, db_session, username):
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    result = []
    res = db_session.query(Account).slice(offset, offset + limit)
    for account in res:
        result.append(account_to_dict(account))
    return result


def get_user_accounts(username, db_session):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(404, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    result = db_session.query(Account).filter(
        Account.person_id == user.person_id).all()
    final_res = []
    for account in result:
        final_res.append(account_to_dict(account))

    return final_res


def delete_all(username, db_session):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(404, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    try:
        db_session.query(Account).filter(
            Account.person_id == user.person_id).delete()
    except:
        raise Http_error(404, Message.MSG20)

    return Http_response(204, True)


def delete(id, db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(404, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    try:
        db_session.query(Account).filter(
            and_(Account.person_id == user.person_id, Account.id == id)
        ).delete()
    except:
        raise Http_error(404, Message.MSG20)

    return Http_response(204, True)


def edit_account_value(account_id, value, db_session):
    account = db_session.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise Http_error(404, Message.MSG20)
    account.value += value
    return account


def get_by_id(id, db_session, username):
    user = check_user(username, db_session)
    if user is None:
        raise Http_error(404, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    try:
        result = db_session.query(Account).filter(
            and_(Account.person_id == user.person_id, Account.id == id)).first()
    except:
        raise Http_error(404, Message.MSG20)

    return account_to_dict(result)


def account_to_dict(account):
    if not isinstance(account,Account):
        raise Http_error(404,Message.INVALID_ENTITY)

    result = model_basic_dict(account)
    model_properties = {
        'person_id':account.person_id,
        'value':account.value,
        'type':str_account_type(account.type)
    }
    result.update(model_properties)
    return result


def add_initial_account(person_id,db_session,username):
    model_instance = Account()
    populate_basic_data(model_instance,username,[])
    model_instance.type = 'Main'
    model_instance.person_id = person_id
    db_session.add(model_instance)

    return model_instance
