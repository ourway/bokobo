from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add,delete,edit


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/rates/<id>', 'PUT', edit, apply=data_plus_wrappers)
    app.route('/rates/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/rates', 'POST', add, apply=data_plus_wrappers)
