from order.models import Order


def get(id, db_session, username=None):
    return db_session.query(Order).filter(Order.id == id).first()

