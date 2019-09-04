from book_library.controller import add_books_to_library
from enums import OrderStatus
from helper import Http_error
from log import logger, LogMsg
from messages import Message
from order.controllers.order_items import recalc_order_price
from repository.item_repo import get_orders_items_internal
from repository.order_repo import get as get_order
from accounts.controller import get as get_account
from financial_transactions.controller import add as add_transaction
from configs import ADMINISTRATORS


def checkout(order_id, data, db_session, username):
    logger.info(LogMsg.START, username)

    preferred_account = data.get('preferred_account', 'Main')
    person_id = data.get('person_id')
    logger.debug(LogMsg.ORDER_CHECKOUT_REQUEST, order_id)
    order = get_order(order_id, db_session)
    logger.debug(LogMsg.ORDER_EXISTS, order_id)
    if order is None:
        logger.error(LogMsg.NOT_FOUND, {'order_id': order_id})
        raise Http_error(404, Message.NOT_FOUND)

    if person_id is not None:
        if order.person_id != person_id and username not in ADMINISTRATORS:
            logger.error(LogMsg.NOT_ACCESSED,
                         {'order_id': order_id, 'username': username})
            raise Http_error(403, Message.ACCESS_DENIED)

    else:

        if order.creator != username and username not in ADMINISTRATORS:
            logger.error(LogMsg.NOT_ACCESSED,
                         {'order_id': order_id, 'username': username,
                          'order_creator': order.creator})
            raise Http_error(403, Message.ACCESS_DENIED)

    logger.debug(LogMsg.GETTING_ACCOUNT_PERSON, {'person_id': order.person_id})
    account = get_account(order.person_id, preferred_account, db_session)
    if account is None:
        logger.error(LogMsg.USER_HAS_NO_ACCOUNT,
                     {'person_id': order.person_id, 'type': preferred_account})
        raise Http_error(404, Message.USER_HAS_NO_ACCOUNT)

    logger.debug(LogMsg.ORDER_CALC_PRICE,{'order_id',order_id})
    order_price = recalc_order_price(order_id, db_session)
    logger.debug(LogMsg.ORDER_CHECK_ACCOUNT_VALUE)
    if account.value < order_price:
        logger.error(LogMsg.ORDER_LOW_BALANCE,{'order_price':order_price,'account_value':account.value})
        raise Http_error(402, Message.INSUFFICIANT_BALANCE)

    account.value -= order_price

    transaction_data = {'account_id': account.id, 'debit': order_price}

    add_transaction(transaction_data, db_session)

    order.status = OrderStatus.Invoiced
    logger.debug(LogMsg.ORDER_INVOICED,order_id)


    order_items = get_orders_items_internal(order_id, db_session)
    logger.debug(LogMsg.ORDER_GETTING_ITEMS,{'order_id':order_id})
    book_list = []
    for item in order_items:
        book_list.append(item.book_id)

    add_books_to_library(order.person_id, book_list, db_session)
    data.update({'order_price': order_price})
    logger.debug(LogMsg.ORDER_ITEMS_ADDED_TO_LIB)
    logger.info(LogMsg.END)
    return data
