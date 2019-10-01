from helper import check_auth, inject_db, jsonify, pass_data
from .controllers import group,group_user


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/groups', 'POST', group.add, apply=data_plus_wrappers)
    app.route('/groups/_search', 'POST', group.search_group, apply=data_plus_wrappers)
    app.route('/groups/<id>', 'DELETE', group.delete, apply=[check_auth, inject_db])
    app.route('/groups/<id>', 'GET', group.get, apply=wrappers)
    app.route('/groups/<id>', 'PUT', group.edit, apply=data_plus_wrappers)


    app.route('/group-users', 'POST', group_user.add_users_to_groups, apply=data_plus_wrappers)
    app.route('/group-users/remove-users', 'POST', group_user.delete_users_from_groups, apply=data_plus_wrappers)
    app.route('/group-users/<id>', 'DELETE', group_user.delete, apply=[check_auth, inject_db])
    app.route('/group-users/<id>', 'GET', group_user.get, apply=wrappers)
    app.route('/group-users/group/<group_id>', 'GET', group_user.get_by_group, apply=wrappers)
    app.route('/group-users/group', 'POST', group_user.add_group_by_users, apply=data_plus_wrappers)
