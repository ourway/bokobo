from .save_file import upload_files
from helper import check_auth, inject_db, jsonify, pass_data


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/upload', 'POST', upload_files, apply=data_plus_wrappers)