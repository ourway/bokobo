import logging

from financial_transactions.models import Transaction
from helper import Http_error, populate_basic_data, Http_response, model_to_dict
from log import LogMsg
from messages import Message
from repository.account_repo import get_account


def add(data, db_session, username=None):
    logging.info(LogMsg.START)

    if data.get('credit') and data.get('debit'):
        raise Http_error(400,Message.CREDIT_DEBIT_ERROR)

    account_id = data.get('account_id')
    account = get_account(account_id, db_session)
    if account is None:
        raise Http_error(404, Message.NOT_FOUND)

    model_instance = Transaction()

    populate_basic_data(model_instance, username)
    model_instance.account_id = account_id
    model_instance.credit = data.get('credit')
    model_instance.debit = data.get('debit')

    db_session.add(model_instance)

    return model_instance


def get(id, db_session,username=None):
    return db_session.query(Transaction).filter(
        Transaction.account_id == id).order_by(
        Transaction.creation_date.desc()).all()


def get_all(data, db_session, username):
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    result = db_session.query(Transaction).order_by(
        Transaction.creation_date.desc()).slice(offset, offset + limit)
    res =[]
    for item in result:
        res.append(model_to_dict(item))

    return res

def delete(id, db_session,username=None):


    try:
        db_session.query(Transaction).filter( Transaction.id == id).delete()
    except:
        raise Http_error(404, Message.NOT_FOUND)

    return Http_response(204, True)



