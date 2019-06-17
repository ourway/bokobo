from user.models import User


def check_user(username, db_session):
    return db_session.query(User).filter(User.username == username).first()