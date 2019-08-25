from helper import check_auth, inject_db, jsonify, pass_data
from .controller import get_personal_library,delete


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/library', 'GET', get_personal_library, apply=wrappers)
    app.route('/library/<id>', 'DELETE', delete,
              apply=[check_auth, inject_db])