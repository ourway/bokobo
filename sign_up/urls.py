from helper import check_auth, inject_db, jsonify, pass_data
from .fast_signup import signup


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/sign-up', 'POST', signup, apply=[pass_data ,inject_db, jsonify])