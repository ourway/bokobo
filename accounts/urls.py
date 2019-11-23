from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, delete, delete_all, get_by_id, get_all, \
    get_user_accounts, get_person_accounts, edit, edit_by_person


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/accounts/<id>', 'GET', get_by_id, apply=wrappers)
    app.route('/accounts/person/<person_id>', 'GET', get_person_accounts,
              apply=wrappers)
    app.route('/accounts/<id>', 'PUT', edit, apply=data_plus_wrappers)
    app.route('/accounts/user/_search', 'POST', get_user_accounts, apply=data_plus_wrappers)
    app.route('/accounts/_search', 'POST', get_all, apply=data_plus_wrappers)
    app.route('/accounts', 'POST', add, apply=data_plus_wrappers)
    app.route('/accounts/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/accounts', 'DELETE', delete_all, apply=[check_auth, inject_db])
    app.route('/accounts', 'PUT', edit_by_person, apply=data_plus_wrappers)

