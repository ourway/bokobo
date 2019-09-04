from book_library.controller import is_book_in_library
from prices.controller import get_book_price_internal, calc_net_price
from repository.user_repo import check_user
from order.models import OrderItem
from repository.order_repo import get as get_order
from repository.book_repo import get as get_book
from books.controllers.book import get as get_book_dict
from helper import Http_error, populate_basic_data, Http_response, \
    check_schema, edit_basic_data, value, model_to_dict, model_basic_dict
from log import LogMsg, logger
from messages import Message
from configs import ONLINE_BOOK_TYPES,ADMINISTRATORS
from repository.order_repo import order_to_dict,get_order_dict

administrator_users = ADMINISTRATORS


def add_orders_items(order_id, items, db_session, username):
    logger.info(LogMsg.START,username)
    total_price = 0.00
    for item in items:
        item['order_id'] = order_id
        item_instance = add(item, db_session, username)
        total_price +=item_instance.net_price

        logger.debug(LogMsg.ORDER_ITEM_ADDDED_TO_ORDER,item_to_dict(item,db_session))

    logger.debug(LogMsg.ORDER_TOTAL_PRICE,total_price)
    logger.info(LogMsg.END)

    return total_price


def add(data, db_session, username):
    logger.info(LogMsg.START,username)

    check_schema(['book_id', 'count', 'order_id'], data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)
    book_id = data.get('book_id')

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
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
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    model_instance.order_id = data.get('order_id')
    model_instance.book_id = book_id
    model_instance.count = data.get('count')
    # TODO discount not imposed yet
    model_instance.discount = data.get('discount',0.0)
    model_instance.description = data.get('description')
    model_instance.price_detail = data.get('price_detail')

    model_instance.unit_price = get_book_price_internal(model_instance.book_id,
                                                        db_session)
    logger.debug(LogMsg.ORDER_ITEM_UNIT_PRICE,model_instance.unit_price)

    model_instance.net_price = calc_net_price(model_instance.unit_price,
                                              model_instance.count,
                                              model_instance.discount)
    logger.debug(LogMsg.ORDER_ITEM_NET_PRICE,model_instance.net_price)

    db_session.add(model_instance)
    logger.info(LogMsg.END)

    return model_instance


def get(id, db_session, username=None):
    logger.info(LogMsg.START)
    item = db_session.query(OrderItem).filter(
        OrderItem.id == id).first()
    return item_to_dict(item,db_session)


def get_all(data, db_session, username=None):
    logger.info(LogMsg.START)
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    if username not in administrator_users:
        logger.error(LogMsg.NOT_ACCESSED,username)
        raise Http_error(403, Message.ACCESS_DENIED)

    result = db_session.query(OrderItem).order_by(
        OrderItem.creation_date.desc()).slice(offset, offset + limit)
    res = []
    for item in result:
        res.append(item_to_dict(item,db_session))
    logger.debug(LogMsg.GET_SUCCESS,res)

    logger.info(LogMsg.END)
    return res


def get_orders_items(order_id, db_session, username=None):
    logger.info(LogMsg.START)

    result = db_session.query(OrderItem).filter(
        OrderItem.order_id == order_id).all()
    final_res = []
    for item in result:
        final_res.append(item_to_dict(item,db_session))
    logger.debug(LogMsg.ORDERS_ITEMS,final_res)
    logger.info(LogMsg.END)

    return final_res


def delete(id, db_session, username=None):
    logger.info(LogMsg.START)

    order_item = get(id, db_session)
    if order_item is None:
        logger.error(LogMsg.NOT_FOUND,{'order_item_id':id})
        raise Http_error(404, Message.NOT_FOUND)
    if order_item.creator != username and username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED,username)
        raise Http_error(403, Message.ACCESS_DENIED)
    order_id = order_item.order_id

    try:
        db_session.delete(order_item)
        logger.debug(LogMsg.ORDER_ITEM_DELETED,id)
        order = calc_total_price_order(order_id, db_session)
        logger.debug(LogMsg.ORDER_CALC_PRICE,order_to_dict(order,db_session,username))
    except:
        logger.exception(LogMsg.DELETE_FAILED,exc_info=True)
        raise Http_error(404, Message.DELETE_FAILED)
    logger.info(LogMsg.END)

    return Http_response(204, True)


def delete_orders_items_internal(order_id, db_session):
    logger.info(LogMsg.START)
    try:
        logger.debug(LogMsg.ORDER_ITEMS_DELETE,{'order_id':order_id})
        db_session.query(OrderItem).filter(
            OrderItem.order_id == order_id).delete()
    except:
        logger.exception(LogMsg.DELETE_FAILED,exc_info=True)
        raise Http_error(404, Message.NOT_FOUND)
    logger.info(LogMsg.END)

    return Http_response(204, True)


def edit(id, data, db_session, username=None):
    logger.info(LogMsg.START)

    model_instance = get(id, db_session)
    logger.debug(LogMsg.MODEL_GETTING,{'order_item_id':id})

    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND,{'order_item_id':id})
        raise Http_error(404, Message.NOT_FOUND)
    if model_instance.creator != username or username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED,username)
        raise Http_error(403, Message.ACCESS_DENIED)

    if 'id' in data:
        del data['id']

    if username not in ADMINISTRATORS:
        if 'unit_price' in data:
            del data['unit_price']
        if 'net_price' in data:
            del data['net_price']
        if 'order_id' in data:
            del data['order_id']
        if 'book_id' in data:
            del data['book_id']

    try:
        for key, value in data.items():
            # TODO  if key is valid attribute of class
            setattr(model_instance, key, value)

        edit_basic_data(model_instance, username)

        model_instance.unit_price = get_book_price_internal(
            model_instance.book_id,
            db_session)
        logger.debug(LogMsg.ORDER_ITEM_UNIT_PRICE, model_instance.unit_price)

        model_instance.net_price = calc_net_price(model_instance.unit_price,
                                                  model_instance.count,
                                                  model_instance.discount)
        logger.debug(LogMsg.ORDER_ITEM_NET_PRICE,model_instance.net_price)

    except:
        logger.exception(LogMsg.EDIT_FAILED,exc_info=True)
        raise Http_error(404, Message.DELETE_FAILED)

    order = calc_total_price_order(model_instance.order_id,db_session)
    logger.debug(LogMsg.ORDER_CALC_PRICE, order_to_dict(order,db_session,username))

    logger.info(LogMsg.END)

    return model_instance


def calc_total_price_order(order_id, db_session):
    logger.info(LogMsg.START)

    items = get_orders_items(order_id,db_session)
    order_price = 0.0
    for item in items:
        order_price +=item.net_price
    order = get_order(order_id,db_session)
    order.total_price = order_price
    logger.info(LogMsg.END)

    return  order


def recalc_order_price(order_id, db_session):
    logger.info(LogMsg.START)

    items = get_orders_items(order_id,db_session)
    order_price = 0.0
    for item in items:
        book_price = get_book_price_internal(item.book_id,db_session)
        if item.unit_price!=book_price:
            item.unit_price = book_price
            item.net_price = calc_net_price(book_price,item.count,
                                              item.discount)
        order_price +=item.net_price
    logger.info(LogMsg.END)

    return order_price


def item_to_dict(item,db_session):
    if not isinstance(item,OrderItem):
        raise Http_error(404,Message.INVALID_ENTITY)

    result = model_basic_dict(item)

    model_props = {
        'book_id':item.book_id,
        'order_id': item.order_id,
        'description': item.description,
        'unit_price': item.unit_price,
        'discount': item.discount,
        'net_price': item.net_price,
        'count': item.count,
        'price_detail':item.price_detail,
        'book': get_book_dict(item.book_id, db_session),
        'order':get_order_dict(item.order_id, db_session)

    }
    result.update(model_props)
    return result