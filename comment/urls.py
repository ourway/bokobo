from helper import check_auth, inject_db, jsonify, pass_data
from  . import controller as comment


def call_router(app):
    readonly_wrappers = [inject_db, jsonify]
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/comments/<id>', 'GET', comment.get, apply=wrappers)
    app.route('/comments/book/<book_id>', 'GET', comment.get_book_comments, apply=wrappers)
    app.route('/comments/book/<book_id>', 'DELETE', comment.delete_book_comments, apply=[check_auth, inject_db])
    app.route('/comments/<id>', 'DELETE', comment.delete, apply=[check_auth, inject_db])
    app.route('/comments', 'POST', comment.add, apply=data_plus_wrappers)