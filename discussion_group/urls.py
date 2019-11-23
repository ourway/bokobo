from helper import check_auth, inject_db, jsonify, pass_data
from .controllers import discussion_group_member,discussuion_group


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/discussion-groups', 'POST', discussuion_group.add, apply=data_plus_wrappers)
    app.route('/discussion-groups/_search', 'POST', discussuion_group.search_group, apply=data_plus_wrappers)
    app.route('/discussion-groups/<id>', 'DELETE', discussuion_group.delete, apply=[check_auth, inject_db])
    app.route('/discussion-groups/<id>', 'GET', discussuion_group.get, apply=wrappers)
    app.route('/discussion-groups/<id>', 'PUT', discussuion_group.edit, apply=data_plus_wrappers)


    app.route('/group-members', 'POST', discussion_group_member.add_disscussuion_members, apply=data_plus_wrappers)
    app.route('/group-members/remove-members/<group_id>', 'POST', discussion_group_member.delete_group_members, apply=[check_auth, inject_db])
    app.route('/group-members/<id>', 'DELETE', discussion_group_member.delete, apply=[check_auth, inject_db])
    app.route('/group-members/<id>', 'GET', discussion_group_member.get, apply=wrappers)
    app.route('/group-members/<id>', 'PUT', discussion_group_member.edit, apply=data_plus_wrappers)
    app.route('/group-members/groups', 'GET', discussion_group_member.user_discuss_groups, apply=wrappers)

