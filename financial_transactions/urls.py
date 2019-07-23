from helper import check_auth, inject_db, jsonify, pass_data
from .controller import delete, get, get_all, add


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/transactions/<id>', 'GET', get, apply=wrappers)
    app.route('/transactions/_search', 'POST', get_all, apply=data_plus_wrappers)
    app.route('/transactions/<id>', 'DELETE', delete,apply=[check_auth, inject_db])
    # app.route('/transactions', 'POST', add,apply=data_plus_wrappers)
