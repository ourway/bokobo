from configs import ADMINISTRATORS
from enums import OrderStatus
from order.controllers.order_items import add_orders_items, \
    delete_orders_items_internal
from repository.user_repo import check_user
from order.models import Order
from helper import Http_error, populate_basic_data, Http_response, \
    model_to_dict, check_schema, edit_basic_data, value, model_basic_dict
from log import LogMsg, logger
from messages import Message
from user.controllers.person import get as get_person

administrator_users = value('administrator_users', ['admin'])


def add(data, db_session, username):
    logger.info(LogMsg.START, username)

    check_schema(['items'], data.keys())

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_ACCOUNT, username)
        raise Http_error(400, Message.Invalid_persons)

    model_instance = Order()

    populate_basic_data(model_instance, username)
    if 'person_id' in data :
        if username not in ADMINISTRATORS and user.person_id!=data.get('person_id'):
            logger.error(LogMsg.NOT_ACCESSED,'user can not add order for others')
            raise Http_error(403,Message.ACCESS_DENIED)
        person_id = data.get('person_id')
    else:
        person_id = user.person_id
    model_instance.person_id = person_id

    db_session.add(model_instance)
    item_data = {}
    item_data['items']= data.get('items')
    item_data['person_id'] = person_id
    logger.debug(LogMsg.ORDER_ADD_ITEMS, data.get('items'))
    model_instance.total_price = add_orders_items(model_instance.id,
                                                  item_data, db_session,
                                                  username)
    order_dict = order_to_dict(model_instance, db_session, username)
    logger.debug(LogMsg.ORDER_ADD, order_dict)
    logger.info(LogMsg.END)
    return order_dict


def get(id, db_session, username=None):
    logger.info(LogMsg.START, username)
    result = db_session.query(Order).filter(Order.id == id).first()
    return order_to_dict(result, db_session, username)


def internal_get(id, db_session):
    return db_session.query(Order).filter(Order.id == id).first()


def get_all(data, db_session, username=None):
    logger.info(LogMsg.START, username)

    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    if username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, username)
        raise Http_error(403, Message.ACCESS_DENIED)

    result = db_session.query(Order).order_by(
        Order.creation_date.desc()).slice(offset, offset + limit)
    res = []
    for item in result:
        res.append(order_to_dict(item, db_session, username))
    logger.info(LogMsg.END)

    return res


def get_user_orders(data, db_session, username=None):
    logger.info(LogMsg.START, username)

    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON, username)
        raise Http_error(400, Message.Invalid_persons)

    result = db_session.query(Order).filter(
        Order.person_id == user.person_id).order_by(
        Order.creation_date.desc()).slice(offset, offset + limit)
    res = []
    for item in result:
        res.append(order_to_dict(item, db_session, username))
    logger.debug(LogMsg.ORDER_USER_ORDERS, res)
    logger.info(LogMsg.END)

    return res


def get_person_orders(data, db_session, username=None):
    logger.info(LogMsg.START, username)

    offset = data.get('offset', 0)
    limit = data.get('limit', 20)
    filter = data.get('filter', None)
    if filter is None:
        logger.error(LogMsg.DATA_MISSING, 'filter')
        raise Http_error(400, Message.MISSING_REQUIERED_FIELD)
    person_id = filter.get('person')

    result = db_session.query(Order).filter(
        Order.person_id == person_id).order_by(
        Order.creation_date.desc()).slice(offset, offset + limit)
    res = []
    for item in result:
        res.append(order_to_dict(item, db_session, username))
    logger.debug(LogMsg.ORDER_USER_ORDERS, res)
    logger.info(LogMsg.END)
    return res


def delete(id, db_session, username=None):
    logger.info(LogMsg.START, username)

    order = internal_get(id, db_session)
    if order is None:
        logger.error(LogMsg.NOT_FOUND, {'order_id': id})
        raise Http_error(404, Message.NOT_FOUND)
    if order.creator != username and username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, username)
        raise Http_error(403, Message.ACCESS_DENIED)
    if order.status == OrderStatus.Invoiced:
        logger.error(LogMsg.ORDER_NOT_EDITABLE,
                     order_to_dict(order, db_session, username))
        raise Http_error(403, Message.ORDER_INVOICED)

    try:
        logger.debug(LogMsg.ORDER_ITEMS_DELETE, {'order_id': id})
        delete_orders_items_internal(order.id, db_session)
        logger.debug(LogMsg.ORDER_DELETE, {'order_id': id})
        db_session.delete(order)
    except:
        logger.exception(LogMsg.DELETE_FAILED, exc_info=True)
        raise Http_error(404, Message.DELETE_FAILED)
    logger.info(LogMsg.END)
    return Http_response(204, True)


def edit(id, data, db_session, username=None):
    logger.info(LogMsg.START, username)
    model_instance = internal_get(id, db_session)
    logger.debug(LogMsg.ORDER_CHECK, {'order_id': id})
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'order_id': id})
        raise Http_error(404, Message.NOT_FOUND)
    if model_instance.creator != username and username not in ADMINISTRATORS:
        logger.error(LogMsg.NOT_ACCESSED, username)
        raise Http_error(403, Message.ACCESS_DENIED)
    if model_instance.status == OrderStatus.Invoiced:
        logger.error(LogMsg.ORDER_NOT_EDITABLE, {'order_id': id})
        raise Http_error(403, Message.ORDER_INVOICED)

    user = check_user(username,db_session)
    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(404,Message.INVALID_USER)

    if 'id' in data:
        del data['id']
    if 'status' in data:
        del data['status']

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    if 'items' in data:
        item_data = {}
        item_data['items'] = data.get('items')
        if 'person_id' in data:
            item_data['person_id'] = data.get('person_id')
        else:
            item_data['person_id'] = user.person_id
        logger.debug(LogMsg.ORDER_ITEMS_DELETE, {'order_id': id})
        delete_orders_items_internal(model_instance.id, db_session)
        logger.debug(LogMsg.ORDER_ADD_ITEMS, {'order_id': id})
        model_instance.total_price = add_orders_items(model_instance.id
                                                      , item_data,
                                                      db_session, db_session)
    edit_basic_data(model_instance, username)
    order_dict = order_to_dict(model_instance, db_session, username)
    logger.debug(LogMsg.MODEL_ALTERED, order_dict)

    logger.info(LogMsg.END)
    return order_dict


def edit_status_internal(id, status, db_session, username=None):
    logger.info(LogMsg.START, username)

    model_instance = internal_get(id, db_session)
    logger.debug(LogMsg.ORDER_CHECK, {'order_id': id})
    if model_instance is None:
        logger.error(LogMsg.NOT_FOUND, {'order_id': id})
        raise Http_error(404, Message.NOT_FOUND)

    try:
        model_instance.status = status
        edit_basic_data(model_instance, username)

    except:
        logger.exception(LogMsg.EDIT_FAILED, exc_info=True)
        raise Http_error(404, Message.DELETE_FAILED)
    logger.info(LogMsg.END)
    return model_instance


def order_to_dict(order, db_session, username=None):
    if not isinstance(order, Order):
        raise Http_error(404, Message.INVALID_ENTITY)

    result = model_basic_dict(order)

    model_props = {
        'person_id': order.person_id,
        'price_detail': order.price_detail,
        'description': order.description,
        'total_price': order.total_price,
        'status': order.status.name,
        'person': get_person(order.person_id, db_session, username)
    }
    result.update(model_props)
    return result
