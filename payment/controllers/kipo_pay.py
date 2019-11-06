from bottle import request

from check_permission import get_user_permissions, has_permission
from enums import Permissions
from financial_transactions.controller import internal_add as transaction_add
from helper import Http_error, value, check_schema, populate_basic_data, \
    model_to_dict, Http_response, edit_basic_data
from log import logger, LogMsg
from messages import Message
from payment.controllers.payment import add_payment
from .payment import get as get_payment
from repository.account_repo import edit_persons_main_account
from repository.user_repo import check_user
from payment.KipoKPG import KipoKPG

"""
    Initial Kipo Library and craete object from KipoKPG class
    Merchant key is merchant phone number
"""
merchant_key = value('kipo_merchant_key', None)
if merchant_key is None:
    logger.error(LogMsg.PAYMENT_FAILED_KIPO, {'merchant_key': merchant_key})
    raise Http_error(400, Message.PAYMENT_FAILED)

kipo = KipoKPG(merchant_key)

"""
    Replace "YOUR CALLBACK URL" and "AMOUNT" with what you want
    kpg_initiate return a Dictionary 
    Successful - {"status": True, "shopping_key": SHOPING_KEY}
    Failed - {"status": false, "message": ERROR_CODE}
"""
base_url = value('app_server_address', 'http://localhost:7000')


def pay_by_kipo(data, db_session, username):
    logger.info(LogMsg.START, username)

    check_schema(['person_id', 'amount'], data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)

    person_id = data.get('person_id')

    user = check_user(username, db_session)

    per_data = {}
    permissions, presses = get_user_permissions(username, db_session)
    if user.person_id == person_id:
        per_data.update({Permissions.IS_OWNER.value: True})
    has_permission(
        [Permissions.PAYMENT_ADD_PREMIUM, Permissions.PAYMENT_ADD_PRESS],
        permissions,None,per_data)
    logger.debug(LogMsg.PERMISSION_VERIFIED)

    kpg_initiate = kipo.kpg_initiate(data.get('amount'),
                                     base_url + '/payment_recieve')

    if kpg_initiate['status']:
        """
            Store kpg_initiate["shopping_key"] to session to verfiy
            payment after user came back from gateway
    
            Call render_form function to render a html form and send
            user to Kipo KPG Gateway (you can create this form manually
            where you want - form example is at the end of Quick Start
        """
        logger.debug(LogMsg.KIPO_PAYMENT_INITIATED, kpg_initiate)
        data.update(
            {'agent': 'kipo', 'shopping_key': kpg_initiate.get('shopping_key'),
             'reference_code': kipo.get_referent_code(),
             'details': kpg_initiate})
        logger.debug(LogMsg.ADDING_PAYMENT_ENTITY, data)
        payment = add_payment(data, db_session, username)
        logger.debug(LogMsg.PAYMENT_ADDED, model_to_dict(payment))

        kipo.render_form(kpg_initiate['shopping_key'])
    else:
        """
            Show error to user
    
            You can call getErrorMessage and send error code to that as input
            and get error message
            kipo.get_error_message(ERROR_CODE)
        """
        logger.error(LogMsg.PAYMENT_FAILED_KIPO, kpg_initiate)
        error = kipo_error_code(kpg_initiate['code'])
        raise Http_error(402, error)
    return kpg_initiate


def recieve_payment(db_session, **kwargs):
    my_dict = request.query.decode()
    data = my_dict.dict
    if data is None:
        logger.error(LogMsg.PAYMENT_DATA_NOT_RECIEVED)
        raise Http_error(404, Message.PAYMENT_FAILED)
    status = data.get('status')
    if status is not None and status[0] == '0':
        logger.error(LogMsg.PAYMENT_CANCELED, data)
        raise Http_error(402, Message.PAYMENT_CANCELED)
    if status is not None and status[0] == '1':
        shopping_key = data.get('sk')[0]
        inquiry = kipo.kpg_inquery(shopping_key)
        print(inquiry)
        if not inquiry.get('status'):
            logger.error(LogMsg.PAYMENT_INQUIRY_NOT_VALID, inquiry)
            error = kipo_error_code(inquiry['code'])
            raise Http_error(402, error)
        payment = get_payment(shopping_key, db_session)
        if payment is None:
            logger.error(LogMsg.PAYMENT_NOT_FOUND, shopping_key)
            raise Http_error(402, Message.INVALID_SHOPPING_KEY)
        if payment.used:
            logger.error(LogMsg.PAYMENT_ALREADY_USED, model_to_dict(payment))
            raise Http_error(402, Message.PAYMENT_ALREADY_CONSIDERED)

        if payment.amount != inquiry.get('amount'):
            logger.error(LogMsg.PAYMENT_INQUIRY_AMOUNT_INVALID,
                         {'payment': model_to_dict(payment),
                          'inquiry': inquiry})
            raise Http_error(402, Message.PAYMENT_INQUIRY_NOT_VALID)

        # TODO add transaction  and account charge
        account = edit_persons_main_account(payment.person_id, payment.amount,
                                            db_session)
        logger.debug(LogMsg.ACCOUNT_VALUE_EDITED, model_to_dict(account))

        transaction_data = {'account_id': account.id, 'credit': payment.amount,
                            'payment_details': model_to_dict(payment)}

        transaction = transaction_add(transaction_data, db_session)
        logger.debug(LogMsg.TRANSACTION_ADDED, model_to_dict(transaction))

        payment.used = True
        payment.reference_code = inquiry.get('referent_code')
        edit_basic_data(payment, None)
        logger.debug(LogMsg.PAYMENT_UPDATED_TO_USED, model_to_dict(payment))

    logger.info(LogMsg.END)
    return {'msg': 'successful'}


def kipo_error_code(error_code):
    exchange_code = {
        -1: 'recheck_information',
        -2: 'analyzing_error',
        -3: 'server_connection_error',
        -4: 'sending_data_error',
        -5: 'payment_canceled',
        -6: 'buyer_cell_no_error',
        -7: 'minimum_payment_error',
        -8: 'maximum_payment_error',
        -9: 'payment_serial_error'
    }
    if error_code not in exchange_code.keys():
        logger.error(LogMsg.NOT_FOUND, {'kipo_error_code': error_code})
        return 'PAYMENT_FAILED'
    return exchange_code.get(error_code)
