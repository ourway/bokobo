from check_permission import get_user_permissions, has_permission
from enums import Permissions
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
    model_instance.details.update({'call_back_url':data.get('call_back_url')})
    model_instance.order_details = data.get('order_details')
    model_instance.shopping_key = data.get('shopping_key')
    model_instance.reference_code = data.get('reference_code')
    model_instance.used = False
    model_instance.status = 'SendToBank'


    db_session.add(model_instance)
    logger.debug(LogMsg.DB_ADD, model_to_dict(model_instance))

    return model_instance


def get(shopping_id, db_session):
    return db_session.query(Payment).filter(
        Payment.shopping_key == shopping_id).first()


def get_all(data,db_session,username):
    logger.info(LogMsg.START,username)
    if data.get('sort') is None:
        data['sort'] = ['creation_date-']

    permissions, presses = get_user_permissions(username, db_session)
    has_permission(
        [Permissions.PAYMENT_GET_PREMIUM], permissions)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    result = Payment.mongoquery(
        db_session.query(Payment)).query(
        **data).end().all()

    logger.info(LogMsg.END)
    return result

