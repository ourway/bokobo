import logging

from enums import OrderStatus
from order.controllers.order_items import add_orders_items, \
    delete_orders_items_internal
from repository.user_repo import check_user
from order.models import Order
from helper import Http_error, populate_basic_data, Http_response, \
    model_to_dict, check_schema, edit_basic_data, value, model_basic_dict
from log import LogMsg
from messages import Message

administrator_users = value('administrator_users', ['admin'])


def add(data, db_session, username):
    logging.info(LogMsg.START)

    check_schema(['items'], data.keys())

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    model_instance = Order()

    populate_basic_data(model_instance, username)
    if 'person_id' in data:
        person_id = data.get('person_id')
    else:
        person_id=user.person_id
    model_instance.person_id = person_id

    db_session.add(model_instance)

    model_instance.total_price = add_orders_items(model_instance.id, data.get('items'), db_session, username)

    return order_to_dict(model_instance)


def get(id, db_session, username=None):
    result = db_session.query(Order).filter(Order.id == id).first()
    return order_to_dict(result)


def internal_get(id, db_session):
    return db_session.query(Order).filter(Order.id == id).first()

def get_all(data, db_session, username=None):
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    if username not in administrator_users:
        raise Http_error(403, Message.ACCESS_DENIED)

    result = db_session.query(Order).order_by(
        Order.creation_date.desc()).slice(offset, offset + limit)
    res = []
    for item in result:
        res.append(order_to_dict(item))

    return res


def get_user_orders(data, db_session, username=None):
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    result = db_session.query(Order).filter(
        Order.person_id == user.person_id).order_by(
        Order.creation_date.desc()).slice(offset, offset + limit)
    res = []
    for item in result:
        res.append(order_to_dict(item))

    return res


def get_person_orders(data, db_session, username=None):
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)
    filter = data.get('filter',None)
    if filter is None:
        raise Http_error(400,Message.MISSING_REQUIERED_FIELD)
    person_id = filter.get('person')

    result = db_session.query(Order).filter(
        Order.person_id == person_id).order_by(
        Order.creation_date.desc()).slice(offset, offset + limit)
    res = []
    for item in result:
        res.append(order_to_dict(item))

    return res


def delete(id, db_session, username=None):
    order = internal_get(id, db_session)
    if order is None:
        raise Http_error(404, Message.MSG20)
    if order.creator != username:
        raise Http_error(403, Message.ACCESS_DENIED)
    if order.status == OrderStatus.Invoiced:
        raise Http_error(403,Message.ORDER_INVOICED)

    try:
        delete_orders_items_internal(order.id, db_session)
        db_session.delete(order)
    except:
        raise Http_error(404, Message.MSG13)

    return Http_response(204, True)


def edit(id,data, db_session, username=None):
    model_instance = internal_get(id, db_session)

    if model_instance is None:
        raise Http_error(404, Message.MSG20)
    if model_instance.creator != username:
        raise Http_error(403, Message.ACCESS_DENIED)
    if model_instance.status == OrderStatus.Invoiced:
        raise Http_error(403,Message.ORDER_INVOICED)

    if 'id' in data:
        del data['id']
    if 'person_id'in data:
        del data['person_id']
    if 'status'in data:
        del data['status']

    try:
        for key, value in data.items():
            # TODO  if key is valid attribute of class
            setattr(model_instance, key, value)
        if 'items' in data:
            delete_orders_items_internal(model_instance.id, db_session)
            model_instance.total_price = add_orders_items(model_instance.id,
                                                          data.get('items'),
                                                          db_session, username)
        edit_basic_data(model_instance, username)

    except:
        raise Http_error(404, Message.MSG13)

    return order_to_dict(model_instance)


def edit_status_internal(id, status, db_session, username=None):
    model_instance = internal_get(id, db_session)

    if model_instance is None:
        raise Http_error(404, Message.MSG20)

    try:
        model_instance.status = status
        edit_basic_data(model_instance, username)

    except:
        raise Http_error(404, Message.MSG13)

    return model_instance


def order_to_dict(order):
    if not isinstance(order,Order):
        raise Http_error(404,Message.INVALID_ENTITY)

    result = model_basic_dict(order)

    model_props = {
        'person_id':order.person_id,
        'price_detail': order.price_detail,
        'description': order.description,
        'total_price': order.total_price,
        'status': order.status.name
    }
    result.update(model_props)
    return result



