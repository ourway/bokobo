from .controller import add, get, get_all, delete
from helper import check_auth, inject_db, jsonify, pass_data


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/tokens/<id>', 'GET', get, apply=wrappers)
    app.route('/tokens', 'GET', get_all, apply=wrappers)
    app.route('/tokens/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/tokens', 'POST', add, apply=data_plus_wrappers)