from accounts.models import Account


def get_account(account_id, db_session):
    return db_session.query(Account).filter(
        Account.id == account_id).first()
