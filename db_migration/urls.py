from helper import check_auth, inject_db, jsonify, pass_data
from .book import book_press_settling
from .permissions import permissions_to_db


def call_router(app):
    readonly_wrappers = [inject_db, jsonify]
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/book-press-settle', 'GET', book_press_settling, apply=wrappers)
    app.route('/permissions/inject-db', 'POST',permissions_to_db , apply=wrappers)

