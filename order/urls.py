from helper import check_auth, inject_db, jsonify, pass_data
from .controllers import order,order_items,checkout_order


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/orders', 'POST', order.add, apply=data_plus_wrappers)
    app.route('/orders/_search', 'POST', order.get_all, apply=data_plus_wrappers)
    app.route('/orders/<id>', 'DELETE', order.delete, apply=[check_auth, inject_db])
    app.route('/orders/<id>', 'GET', order.get, apply=wrappers)
    app.route('/orders/<id>', 'PUT', order.edit, apply=data_plus_wrappers)
    app.route('/orders/user', 'POST', order.get_user_orders, apply=data_plus_wrappers)
    app.route('/orders/checkout/<order_id>', 'POST', checkout_order.checkout,
              apply=data_plus_wrappers)

    app.route('/order-items', 'POST', order_items.add, apply=data_plus_wrappers)
    app.route('/order-items/_search', 'POST', order_items.get_all, apply=data_plus_wrappers)
    app.route('/order-items/<id>', 'DELETE', order_items.delete, apply=[check_auth, inject_db])
    app.route('/order-items/<id>', 'GET', order_items.get, apply=wrappers)
    app.route('/order-items/<id>', 'PUT', order_items.edit, apply=data_plus_wrappers)
    app.route('/order-items/order/<order_id>', 'GET', order_items.get_orders_items, apply=wrappers)

