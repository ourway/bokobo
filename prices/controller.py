
from .models import Price
from helper import Http_error, populate_basic_data, Http_response, \
    model_to_dict, check_schema
from log import LogMsg, logger
from messages import Message
from repository.book_repo import get as get_book
from configs import ADMINISTRATORS


def add(data, db_session, username):
    logger.info(LogMsg.START)

    check_schema(['price', 'book_id'], data.keys())

    book_id = data.get('book_id')
    get_book(book_id, db_session)
    model_instance = Price()

    populate_basic_data(model_instance, username)
    model_instance.book_id = book_id
    model_instance.price = data.get('price')

    db_session.add(model_instance)

    return model_instance


def get_by_book(book_id, db_session, username=None):
    return db_session.query(Price).filter(Price.book_id == book_id).first()


def get_all(data, db_session, username=None):
    offset = data.get('offset', 0)
    limit = data.get('limit', 20)

    result = db_session.query(Price).order_by(
        Price.creation_date.desc()).slice(offset, offset + limit)
    res = []
    for item in result:
        res.append(model_to_dict(item))

    return res


def get_by_id(id, db_session, username=None):
    return db_session.query(Price).filter(Price.id == id).first()


def delete(id, db_session, username=None):
    logger.info(LogMsg.START,username)

    price = get_by_id(id, db_session)
    if price is None:
        raise Http_error(404, Message.MSG20)
    if price.creator != username or username not in ADMINISTRATORS:
        raise Http_error(403, Message.ACCESS_DENIED)

    try:
        db_session.delete(price)
    except:
        logger.exception(LogMsg.DELETE_FAILED,exc_info=True)
        raise Http_error(404, Message.MSG13)

    logger.info(LogMsg.END)

    return Http_response(204, True)


def edit(id, data, db_session, username=None):
    check_schema(['price'], data.keys())

    model_instance = get_by_id(id, db_session)

    if model_instance is None:
        raise Http_error(404, Message.MSG20)
    if model_instance.creator != username:
        raise Http_error(403, Message.ACCESS_DENIED)

    try:
        model_instance.price = data.get('price')
    except:
        raise Http_error(404, Message.MSG13)

    return model_instance


def internal_edit(book_id, price, db_session):
    model_instance = get_by_book(book_id, db_session)

    if model_instance is None:
        raise Http_error(404, Message.MSG20)

    try:
        model_instance.price = price
    except:
        raise Http_error(404, Message.MSG13)

    return model_instance


def get_book_price_internal(book_id, db_session):
    model_instance = db_session.query(Price).filter(
        Price.book_id == book_id).first()
    if model_instance:
        return model_instance.price
    else:
        return None


def calc_price(data, db_session, username):
    item_prices = []
    total_price = 0.000

    items = data.get('items')
    for item in items:
        book_id = item.get('book_id')
        count = item.get('count', 0)
        discount = item.get('discount', None)
        price_object = get_book_price_internal(book_id, db_session)

        if price_object is None:
            raise Http_error(404, Message.NO_PRICE_FOUND)

        price = price_object.price * count
        net_price = price
        if discount:
            if isinstance(discount, float) and discount < 1:
                effect = 1.000 - discount
                net_price = price * effect
            else:
                raise Http_error(404, Message.DISCOUNT_IS_FLOAT)

        item_info = {'book_id': book_id, 'unit_price': price_object.price,
                     'count': count,'discount':discount, 'net_price': net_price}
        item_prices.append(item_info)
        total_price +=net_price

    return {'items':item_prices,'total_price':total_price}


def calc_net_price(unit_price ,count,discount =0.0):
    if unit_price is None:
        raise Http_error(400,Message.NO_PRICE_FOUND)
    net_price = unit_price * count
    if discount != 0.0:
        if discount<1.00:
            net_price = net_price*(1-discount)
        else:
            raise Http_error(404, Message.DISCOUNT_IS_FLOAT)

    return net_price



