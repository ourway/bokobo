from book_library.controller import is_book_in_library
from prices.controller import get_book_price_internal, calc_net_price
from repository.user_repo import check_user
from order.models import OrderItem
from repository.order_repo import get as get_order
from repository.book_repo import get as get_book
from helper import Http_error, populate_basic_data, Http_response, \
    check_schema, edit_basic_data, value, model_to_dict
from log import LogMsg, logger
from messages import Message
from configs import ONLINE_BOOK_TYPES

administrator_users = value('administrator_users', ['admin'])


def add_orders_items(order_id, items, db_session, username):
    total_price = 0.00
    for item in items:
        item['order_id'] = order_id
        item_instance = add(item, db_session, username)
        total_price +=item_instance.net_price

    return total_price


def add(data, db_session, username):
    logger.info(LogMsg.START)

    check_schema(['book_id', 'count', 'order_id'], data.keys())
    book_id = data.get('book_id')

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    if is_book_in_library(user.person_id, book_id, db_session):
        logger.error(LogMsg.ALREADY_IS_IN_LIBRARY,{'book_id':book_id})
        raise Http_error(409,Message.ALREADY_EXISTS)

    book = get_book(book_id,db_session)
    if book is None:
        logger.error(LogMsg.NOT_FOUND,{'book_id':book_id})
        raise Http_error(404,Message.NOT_FOUND)
    
    if book.type.name in ONLINE_BOOK_TYPES and data.get('count')>1:
        logger.error(LogMsg.BOOK_ONLINE_TYPE_COUNT_LIMITATION)
        raise Http_error(400,Message.ONLINE_BOOK_COUNT_LIMITATION)

    model_instance = OrderItem()

    populate_basic_data(model_instance, username)
    model_instance.order_id = data.get('order_id')
    model_instance.book_id = book_id
    model_instance.count = data.get('count')
    # TODO discount not imposed yet
    model_instance.discount = data.get('discount',0.0)
    model_instance.description = data.get('description')
    model_instance.price_detail = data.get('price_detail')

    model_instance.unit_price = get_book_price_internal(model_instance.book_id,
                                                        db_session)
    model_instance.net_price = calc_net_price(model_instance.unit_price,
                                              model_instance.count,
                                              model_instance.discount)

    db_session.add(model_instance)

    return model_instance


def get(id, db_session, username=None):
    return db_session.query(OrderItem).filter(
        OrderItem.id == id).first()


def get_all(data, db_session, username=None):
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    if username not in administrator_users:
        raise Http_error(403, Message.ACCESS_DENIED)

    result = db_session.query(OrderItem).order_by(
        OrderItem.creation_date.desc()).slice(offset, offset + limit)
    res = []
    for item in result:
        res.append(model_to_dict(item))

    return res


def get_orders_items(order_id, db_session, username=None):
    result = db_session.query(OrderItem).filter(
        OrderItem.order_id == order_id).all()

    return result


def delete(id, db_session, username=None):
    order_item = get(id, db_session)
    if order_item is None:
        raise Http_error(404, Message.NOT_FOUND)
    if order_item.creator != username:
        raise Http_error(403, Message.ACCESS_DENIED)
    order_id = order_item.order_id

    try:
        db_session.delete(order_item)
        calc_total_price_order(order_id, db_session)
    except:
        raise Http_error(404, Message.DELETE_FAILED)

    return Http_response(204, True)


def delete_orders_items_internal(order_id, db_session):
    # items = get_orders_items(order_id,db_session)
    try:
        db_session.query(OrderItem).filter(
            OrderItem.order_id == order_id).delete()
    except:
        raise Http_error(404, Message.NOT_FOUND)
    return Http_response(204, True)


def edit(id, data, db_session, username=None):
    model_instance = get(id, db_session)

    if model_instance is None:
        raise Http_error(404, Message.NOT_FOUND)
    if model_instance.creator != username or username not in administrator_users:
        raise Http_error(403, Message.ACCESS_DENIED)

    if 'id' in data:
        del data['id']
    if 'order_id' in data:
        del data['order_id']
    if 'book_id' in data:
        del data['book_id']

    if username not in administrator_users:
        if 'unit_price' in data:
            del data['unit_price']
        if 'net_price' in data:
            del data['net_price']

    try:
        for key, value in data.items():
            # TODO  if key is valid attribute of class
            setattr(model_instance, key, value)

        edit_basic_data(model_instance, username)

        model_instance.unit_price = get_book_price_internal(
            model_instance.book_id,
            db_session)
        model_instance.net_price = calc_net_price(model_instance.unit_price,
                                                  model_instance.count,
                                                  model_instance.discount)
    except:
        raise Http_error(404, Message.DELETE_FAILED)

    calc_total_price_order(model_instance.order_id,db_session)

    return model_instance


def calc_total_price_order(order_id, db_session):
    items = get_orders_items(order_id,db_session)
    order_price = 0.0
    for item in items:
        order_price +=item.net_price
    order = get_order(order_id,db_session)
    order.total_price = order_price
    return  order


def recalc_order_price(order_id, db_session):
    items = get_orders_items(order_id,db_session)
    order_price = 0.0
    for item in items:
        book_price = get_book_price_internal(item.book_id,db_session)
        if item.unit_price!=book_price:
            item.unit_price = book_price
            item.net_price = calc_net_price(book_price,item.count,
                                              item.discount)
        order_price +=item.net_price

    return order_price