from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add,delete,get_follower_list,get_following_list


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/following-list', 'POST', get_following_list, apply=data_plus_wrappers)
    app.route('/follower-list', 'POST', get_follower_list, apply=data_plus_wrappers)
    app.route('/follow/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/follow', 'POST', add, apply=data_plus_wrappers)
