from helper import check_auth, inject_db, jsonify, pass_data
from celery_works.workers.main_producer import generate_book, check_status


def call_router(app):
    readonly_wrappers = [inject_db, jsonify]
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/generate-book', 'POST', generate_book, apply=[pass_data,jsonify])
    app.route('/generate-book/<id>', 'GET', check_status, apply=[jsonify])
