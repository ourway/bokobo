from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add,get_wish_list,delete_wish_list, delete_books_from_wish_list


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/wish-list/remove-books', 'DELETE', delete_books_from_wish_list, apply=[check_auth, inject_db,pass_data])
    app.route('/wish-list', 'DELETE', delete_wish_list, apply=[check_auth, inject_db])
    app.route('/wish-list', 'POST', add, apply=data_plus_wrappers)
    app.route('/wish-list/_search', 'POST', get_wish_list, apply=data_plus_wrappers)

