from helper import check_auth, inject_db, jsonify, pass_data
from permission.controllers.permission import add,get,get_all,edit,delete,search_permission,permissions_to_db
from permission.controllers import group_permission


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/permissions', 'POST', add, apply=data_plus_wrappers)
    app.route('/permissions', 'GET', get_all, apply=wrappers)
    app.route('/permissions/_search', 'POST', search_permission, apply=data_plus_wrappers)
    app.route('/permissions/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/permissions/<id>', 'GET', get, apply=wrappers)
    app.route('/permissions/<id>', 'PUT', edit, apply=data_plus_wrappers)
    app.route('/permissions/inject-db', 'POST',permissions_to_db , apply=wrappers)



    app.route('/group-permissions', 'POST', group_permission.add_permissions_to_groups, apply=data_plus_wrappers)
    app.route('/group-permissions/filter-group', 'POST', group_permission.get_all, apply=data_plus_wrappers)
    app.route('/group-permissions/_search', 'POST', group_permission.get_by_data, apply=data_plus_wrappers)
    app.route('/group-permissions/<id>', 'DELETE', group_permission.delete, apply=[check_auth, inject_db])
    app.route('/group-permissions/<id>', 'GET', group_permission.get, apply=wrappers)
    app.route('/group-permissions/remove', 'POST', group_permission.delete_permissions_of_groups, apply=data_plus_wrappers)
    app.route('/group-permissions/group', 'POST', group_permission.group_permission_list, apply=data_plus_wrappers)
    app.route('/group-permissions/group/premium-permission/<group_id>', 'POST', group_permission.premium_permission_group, apply=wrappers)
