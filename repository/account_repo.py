from accounts.models import Account
from helper import Http_error
from messages import Message

def get_account(account_id, db_session):
    return db_session.query(Account).filter(
        Account.id == account_id).first()

def edit_account_value(account_id, value, db_session):
    account = db_session.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise Http_error(404, Message.MSG20)
    account.value += value

    return account
