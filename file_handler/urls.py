from .handle_file import upload_files,return_file,delete_multiple_files
from helper import check_auth, inject_db, jsonify, pass_data


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/upload', 'POST', upload_files, apply=data_plus_wrappers)
    app.route('/serve-files/<filename>', 'GET', return_file)
    app.route('/delete-files', 'POST', delete_multiple_files, apply=[pass_data,check_auth,inject_db])
