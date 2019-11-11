from helper import check_auth, inject_db, jsonify, pass_data
from .book import book_press_settling


def call_router(app):
    readonly_wrappers = [inject_db, jsonify]
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/book-press-settle', 'GET', book_press_settling, apply=wrappers)
