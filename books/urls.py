from books.controllers import book, book_roles, book_content
from helper import check_auth, inject_db, jsonify, pass_data


def call_router(app):
    readonly_wrappers = [inject_db, jsonify]
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/books/<id>', 'GET', book.get, apply=readonly_wrappers)
    app.route('/books/_search', 'POST', book.get_all, apply=data_plus_wrappers)
    app.route('/books/<id>', 'DELETE', book.delete_book,
              apply=[check_auth, inject_db])
    app.route('/books', 'POST', book.add_multiple_type_books,
              apply=data_plus_wrappers)
    app.route('/books/_search', 'POST', book.search_book,
              apply=[inject_db, jsonify, pass_data])
    app.route('/books/search-phrase', 'POST', book.search_by_phrase,
              apply=[inject_db, jsonify, pass_data])
    app.route('/books/<id>', 'PUT', book.edit_book, apply=data_plus_wrappers)

    app.route('/books/recommended', 'POST', book.search_by_writer,
              apply=[inject_db, jsonify, pass_data])

    app.route('/books/newest', 'POST', book.newest_books,
              apply=[inject_db, jsonify, pass_data])

    app.route('/books/admin', 'GET', book.book_by_press, apply=wrappers)



    app.route('/book-roles/<id>', 'GET', book_roles.get,
              apply=readonly_wrappers)
    app.route('/books-roles', 'GET', book_roles.get_all,
              apply=readonly_wrappers)
    app.route('/books-roles/<id>', 'DELETE', book_roles.delete,
              apply=[check_auth, inject_db])
    app.route('/books-roles', 'POST', book_roles.add, apply=data_plus_wrappers)
    app.route('/books-roles/multiple-role', 'POST', book_roles.add_book_roles,
              apply=data_plus_wrappers)

    app.route('/book-contents/<id>', 'GET', book_content.get, apply=wrappers)
    app.route('/book-contents/_search', 'POST', book_content.get_all,
              apply=data_plus_wrappers)
    app.route('/book-contents/<id>', 'DELETE', book_content.delete,
              apply=[check_auth, inject_db])
    app.route('/book-contents', 'POST', book_content.add,
              apply=data_plus_wrappers)
    app.route('/book-contents/<id>', 'PUT', book_content.edit,
              apply=data_plus_wrappers)
