from books.controllers import book, book_roles
from helper import check_auth, inject_db, jsonify, pass_data


def call_router(app):
    readonly_wrappers = [inject_db, jsonify]
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/books/<id>', 'GET', book.get, apply=readonly_wrappers)
    app.route('/books', 'GET', book.get_all, apply=readonly_wrappers)
    app.route('/books/<id>', 'DELETE', book.delete, apply=[check_auth, inject_db])
    # app.route('/books', 'POST', book.add, apply=data_plus_wrappers)
    app.route('/books', 'POST', book.add_multiple_type_books, apply=data_plus_wrappers)


    app.route('/book-roles/<id>', 'GET', book_roles.get, apply=readonly_wrappers)
    app.route('/books-roles', 'GET', book_roles.get_all, apply=readonly_wrappers)
    app.route('/books-roles/<id>', 'DELETE', book_roles.delete, apply=[check_auth, inject_db])
    app.route('/books-roles', 'POST', book_roles.add, apply=data_plus_wrappers)
    app.route('/books-roles/multiple-role', 'POST', book_roles.add_book_roles, apply=data_plus_wrappers)


