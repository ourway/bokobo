from helper import check_auth, inject_db, jsonify, pass_data
from .controller import delete, get_by_book, get_all, add, get_by_id, edit


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/prices/<id>', 'GET', get_by_id, apply=wrappers)
    app.route('/prices/book/<book_id>', 'GET', get_by_book, apply=wrappers)
    app.route('/prices/_search', 'POST', get_all, apply=data_plus_wrappers)
    app.route('/prices/<id>', 'DELETE', delete,apply=[check_auth, inject_db])
    app.route('/prices', 'POST', add,apply=data_plus_wrappers)
    app.route('/prices/<id>', 'PUT', edit, apply=data_plus_wrappers)
