from sqlalchemy import and_

from accounts.models import Account
from enums import check_enum, AccountTypes, str_account_type, Permissions
from helper import Http_error, populate_basic_data, model_to_dict, \
    Http_response, model_basic_dict, check_schema
from log import LogMsg
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user
from configs import ADMINISTRATORS
from log import logger
from check_permission import get_user_permissions, has_permission


def add(data, db_session, username):
    logger.debug(LogMsg.START, username)

    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.ACCOUNT_ADD_PREMIUM], permissions)
    check_schema(['person_id','type'],data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)
    check_enum(data.get('type'), AccountTypes)
    logger.debug(LogMsg.ENUM_CHECK,
                 {'enum': data.get('type'), 'reference_enum': 'AccountTypes'})

    user = check_user(username, db_session)
    logger.debug(LogMsg.USER_CHECKING, username)

    if user is None:
        logger.error(LogMsg.INVALID_USER, username)
        raise Http_error(404, Message.INVALID_USER)

    logger.info(LogMsg.USER_XISTS, username)

    if user.person_id is None:
        logger.info(LogMsg.PERSON_NOT_EXISTS, username)

        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.info(LogMsg.PERSON_EXISTS, username)

    type = data.get('type','Main')
    value = data.get('value',0.0)
    person_id = data.get('person_id')

    logger.info(LogMsg.GETTING_USER_ACCOUNTS, type)

    account = get(person_id, type, db_session)
    if account is not None:
        logger.error(LogMsg.ACCOUNT_BY_TYPE_EXISTS, type)

        raise Http_error(409, Message.ALREADY_EXISTS)

    model_instance = Account()

    populate_basic_data(model_instance, username, data.get('tags'))
    logger.debug(LogMsg.POPULATING_BASIC_DATA)

    model_instance.type = type
    model_instance.person_id = person_id
    model_instance.value = value

    db_session.add(model_instance)

    logger.debug(LogMsg.DB_ADD, account_to_dict(model_instance))

    logger.info(LogMsg.END)

    return account_to_dict(model_instance)


def get(person_id, type, db_session):
    logger.info(LogMsg.START)
    logger.debug(LogMsg.GETTING_USER_ACCOUNTS, type)



    try:
        result = db_session.query(Account).filter(
            and_(Account.person_id == person_id, Account.type == type)).first()

        if result:

            logger.debug(LogMsg.GET_SUCCESS, account_to_dict(result))
        else:
            logger.debug(LogMsg.USER_HAS_NO_ACCOUNT, type)

    except:
        logger.error(LogMsg.GET_FAILED,
                     {'person_id': person_id, 'account_type': type},
                     exc_info=True)

        raise Http_error(404, Message.GET_FAILED)

    logger.info(LogMsg.END)

    return result


def get_person_accounts(person_id, db_session, username):
    logger.info(LogMsg.START, username)

    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.ACCOUNT_GET_PREMIUM], permissions)

    rtn = []

    try:
        logger.debug(LogMsg.GETTING_PERSON_ALL_ACCOUNTS, person_id)

        result = db_session.query(Account).filter(
            Account.person_id == person_id).all()
        for item in result:
            rtn.append(account_to_dict(item))
        logger.debug(LogMsg.GET_SUCCESS, rtn)
    except:
        logger.error(LogMsg.GET_FAILED,
                     {'person_id': person_id},
                     exc_info=True)

        raise Http_error(404, Message.GET_FAILED)

    logger.info(LogMsg.END)

    return rtn


def get_all(data, db_session, username):
    logger.info(LogMsg.START, username)
    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.ACCOUNT_GET_PREMIUM], permissions)
    if data.get('sort') is None:
        data['sort'] = ['creation_date-']
    result = []
    try:
        res = Account.mongoquery(
            db_session.query(Account)).query(
            **data).end().all()
        for account in res:
            result.append(account_to_dict(account))
    except:
        logger.error(LogMsg.GET_FAILED,
                     exc_info=True)
        raise Http_error(404, Message.GET_FAILED)

    logger.info(LogMsg.END)

    return result


def get_user_accounts(username, db_session,data):
    logger.info(LogMsg.START, username)

    user = check_user(username, db_session)
    if user is None:
        logger.error(LogMsg.INVALID_USER, username)

        raise Http_error(404, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.PERSON_NOT_EXISTS, username)
        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS, username)

    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    if data.get('filter') is None:
        data.update({'filter':{'person_id':user.person_id}})
    else:
        data['filter'].update({'person_id':user.person_id})

    try:
        result = Account.mongoquery(
            db_session.query(Account)).query(
            **data).end().all()

        final_res = []
        for account in result:
            final_res.append(account_to_dict(account))
        logger.debug(LogMsg.GET_SUCCESS, final_res)


    except:

        logger.error(LogMsg.GET_FAILED,
                     exc_info=True)
        raise Http_error(404, Message.GET_FAILED)

    logger.info(LogMsg.END)

    return final_res


def delete_all(username, db_session):
    logger.info(LogMsg.START, username)

    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.ACCOUNT_DELETE_PREMIUM], permissions)

    user = check_user(username, db_session)
    if user is None:
        logger.error(LogMsg.INVALID_USER, username)

        raise Http_error(404, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.PERSON_NOT_EXISTS, username)

        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS, username)

    try:
        logger.debug(LogMsg.DELETE_USER_ALL_ACCOUNTS, username)

        db_session.query(Account).filter(
            Account.person_id == user.person_id).delete()
    except:
        logger.error(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(404, Message.NOT_FOUND)
    logger.info(LogMsg.END)

    return Http_response(204, True)


def delete(id, db_session, username):
    logger.info(LogMsg.START, username)

    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.ACCOUNT_DELETE_PREMIUM], permissions)

    user = check_user(username, db_session)
    if user is None:
        logger.error(LogMsg.INVALID_USER, username)

        raise Http_error(404, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.PERSON_NOT_EXISTS, username)

        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS, username)

    try:
        logger.debug(LogMsg.DELETE_ACCOUNT_BY_ID, id)
        db_session.query(Account).filter(
            and_(Account.person_id == user.person_id, Account.id == id)
        ).delete()
    except:
        logger.error(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(404, Message.NOT_FOUND)
    logger.info(LogMsg.END)

    return Http_response(204, True)


def edit_account_value(account_id, value, db_session, username=None):
    logger.info(LogMsg.START)

    if username is not None:
        permissions, presses = get_user_permissions(username, db_session)
        has_permission([Permissions.ACCOUNT_EDIT_PREMIUM], permissions)

    logger.debug(LogMsg.EDIT_ACCOUNT_VALUE,
                 {'account_id': account_id, 'value': value})

    logger.debug(LogMsg.GETTING_ACCOUNT_BY_ID, account_id)

    account = db_session.query(Account).filter(Account.id == account_id).first()
    if account is None:
        logger.error(LogMsg.NOT_FOUND, {'account_id': account_id})
        raise Http_error(404, Message.NOT_FOUND)
    account.value += value
    logger.debug(LogMsg.ACCOUNT_VALUE_EDITED, account_id)
    logger.info(LogMsg.END)

    return account_to_dict(account)


def get_by_id(id, db_session, username):
    logger.info(LogMsg.START, username)

    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.ACCOUNT_GET_PREMIUM], permissions)

    user = check_user(username, db_session)
    if user is None:
        logger.error(LogMsg.INVALID_USER, username)

        raise Http_error(404, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.PERSON_NOT_EXISTS, username)

        raise Http_error(404, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS, username)

    try:
        logger.debug(LogMsg.GETTING_ACCOUNT_BY_ID, id)
        result = db_session.query(Account).filter(
            and_(Account.person_id == user.person_id, Account.id == id)).first()
        if result is None:
            logger.debug(LogMsg.ACCOUNT_BY_ID_IS_NOT_FOR_PERSON,
                         {'account_id': id, 'person_id': user.person_id})
    except:
        logger.error(LogMsg.GET_FAILED, exc_info=True)
        raise Http_error(404, Message.NOT_FOUND)
    logger.info(LogMsg.END)

    return account_to_dict(result)


def edit(id, data, db_session, username):
    logger.info(LogMsg.START, username)

    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.ACCOUNT_EDIT_PREMIUM], permissions)

    check_schema(['value'], data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)

    value = data.get('value')
    logger.debug(LogMsg.GETTING_ACCOUNT_BY_ID, id)
    account = db_session.query(Account).filter(Account.id == id).first()
    if account is None:
        logger.error(LogMsg.NOT_FOUND, {'account_id': id})
        raise Http_error(404, Message.NOT_FOUND)
    account.value += value
    logger.debug(LogMsg.EDIT_SUCCESS)
    logger.info(LogMsg.END)

    return account_to_dict(account)


def account_to_dict(account):
    if not isinstance(account, Account):
        raise Http_error(404, Message.INVALID_ENTITY)

    result = model_basic_dict(account)
    model_properties = {
        'person_id': account.person_id,
        'value': account.value,
        'type': str_account_type(account.type)
    }
    result.update(model_properties)
    return result


def add_initial_account(person_id, db_session, username):
    logger.info(LogMsg.START, username)

    logger.debug(LogMsg.ADD_INITIAL_ACCOUNT, person_id)

    model_instance = Account()
    populate_basic_data(model_instance, username, [])
    model_instance.type = 'Main'
    model_instance.person_id = person_id
    db_session.add(model_instance)
    logger.info(LogMsg.END)

    return account_to_dict(model_instance)


def edit_by_person(data, db_session, username):
    logger.info(LogMsg.START, username)

    user = check_user(username, db_session)

    check_schema(['person_id','value'],data.keys())

    permissions, presses = get_user_permissions(username, db_session)
    has_permission([Permissions.ACCOUNT_EDIT_PREMIUM], permissions)

    logger.debug(LogMsg.SCHEMA_CHECKED)

    value = data.get('value')
    type = data.get('type', 'Main')
    person_id = data.get('person_id')

    logger.debug(LogMsg.GETTING_ACCOUNT_PERSON, data)

    account = db_session.query(Account).filter(
        and_(Account.person_id == person_id, Account.type == type)).first()

    if account is None:
        logger.error(LogMsg.NOT_FOUND, {'account_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    permissions, presses = get_user_permissions(username, db_session)
    per_data = {}
    if user.person_id == account.person_id:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission([Permissions.ACCOUNT_EDIT_PREMIUM], permissions, None,
                   per_data)

    account.value += value
    logger.debug(LogMsg.EDIT_SUCCESS)
    logger.info(LogMsg.END)

    return account_to_dict(account)
