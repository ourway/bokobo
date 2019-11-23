from order.models import OrderItem


def get_orders_items_internal(order_id, db_session, username=None):

    result = db_session.query(OrderItem).filter(
        OrderItem.order_id == order_id).all()

    return result