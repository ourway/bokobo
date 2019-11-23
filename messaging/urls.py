from helper import check_auth, inject_db, jsonify, pass_data
from messaging.controllers.message import add, get, get_all, get_group_messages, \
    edit, delete,get_user_unread_messages,get_sender_messages


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/messages', 'POST', add, apply=data_plus_wrappers)
    app.route('/messages/_search', 'POST', get_all,
              apply=data_plus_wrappers)
    app.route('/messages/<id>', 'DELETE', delete,
              apply=[check_auth, inject_db])
    app.route('/messages/<id>', 'GET', get, apply=wrappers)
    app.route('/messages/<id>', 'PUT', edit, apply=data_plus_wrappers)
    app.route('/messages/group/<group_id>', 'POST', get_group_messages, apply=data_plus_wrappers)
    app.route('/messages/direct', 'POST', get_sender_messages, apply=data_plus_wrappers)
    app.route('/messages/unread', 'POST', get_user_unread_messages, apply=data_plus_wrappers)

