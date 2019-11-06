from helper import check_auth, inject_db, jsonify, pass_data
from payment.controllers.kipo_pay import recieve_payment, pay_by_kipo


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/payment_recieve', 'GET', recieve_payment,
              apply=[inject_db, jsonify])
    app.route('/payment_send', 'POST', pay_by_kipo, apply=data_plus_wrappers)
