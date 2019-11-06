from helper import populate_basic_data, model_to_dict
from log import logger, LogMsg
from payment.models import Payment


def add_payment(data, db_session, username):
    logger.info(LogMsg.START, username)

    model_instance = Payment()
    populate_basic_data(model_instance, username)
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.person_id = data.get('person_id')
    model_instance.amount = data.get('amount')
    model_instance.agent = data.get('agent')
    model_instance.details = data.get('details')
    model_instance.order_details = data.get('order_details')
    model_instance.shopping_key = data.get('shopping_key')
    model_instance.reference_code = data.get('reference_code')
    model_instance.used = False

    db_session.add(model_instance)
    logger.debug(LogMsg.DB_ADD, model_to_dict(model_instance))

    return model_instance


def get(shopping_id, db_session):
    return db_session.query(Payment).filter(
        Payment.shopping_key == shopping_id).first()


