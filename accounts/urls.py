from helper import check_auth, inject_db, jsonify, pass_data


def call_router(app):
    readonly_wrappers = [inject_db, jsonify]
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/accounts/<id>', 'GET', comment.get, apply=wrappers)
    app.route('/accounts/<id>', 'PUT', comment.edit, apply=data_plus_wrappers)
    app.route('/accounts/book/<book_id>', 'POST', comment.get_book_accounts,
              apply=data_plus_wrappers)
    app.route('/comments/<id>', 'DELETE', comment.delete,
              apply=[check_auth, inject_db])
    app.route('/comments', 'POST', comment.add, apply=data_plus_wrappers)

    app.route('/comment-actions/reports/<comment_id>', 'GET',
              actions.get_comment_reports, apply=data_plus_wrappers)

    app.route('/comment-actions/like/<comment_id>', 'POST', actions.like,
              apply=[check_auth, inject_db, jsonify])
    app.route('/comment-actions/like/<comment_id>', 'DELETE', actions.dislike,
              apply=[check_auth, inject_db])
    app.route('/comment-actions/report/<comment_id>', 'POST', actions.report,
              apply=data_plus_wrappers)
    app.route('/comment-actions/report/<comment_id>', 'DELETE',
              actions.dis_report, apply=[check_auth, inject_db])
