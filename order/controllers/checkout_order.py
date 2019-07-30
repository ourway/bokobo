from book_library.controller import add_books_to_library
from enums import OrderStatus
from helper import Http_error
from messages import Message
from order.controllers.order_items import recalc_order_price, get_orders_items
from repository.account_repo import edit_account_value
from .order import get as get_order
from accounts.controller import get as get_account
from financial_transactions.controller import add as add_transaction


def checkout(order_id, data, db_session, username):
    preferred_account = data.get('preferred_account', 'Main')

    order = get_order(order_id, db_session)
    if order is None:
        raise Http_error(404, Message.MSG20)

    if order.creator != username:
        raise Http_error(403, Message.ACCESS_DENIED)

    account = get_account(order.person_id, preferred_account, db_session)

    order_price = recalc_order_price(order_id, db_session)
    if account.value < order_price:
        raise Http_error(402, Message.INSUFFICIANT_BALANCE)

    account.value -= order_price

    transaction_data = {'account_id': account.id, 'debit': order_price}

    add_transaction(transaction_data, db_session)

    order.status = OrderStatus.Invoiced

    order_items = get_orders_items(order_id, db_session)
    book_list = []
    for item in order_items:
        book_list.append(item.book_id)

    library = add_books_to_library(order.person_id, book_list, db_session)

    return library
