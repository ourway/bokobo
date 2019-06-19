from bottle import static_file, response

from helper import file_mime_type, value

save_path = value('save_path')

def return_file(filename, **kwargs):
    response.body = static_file(filename, root=save_path)
    file_path = save_path + '/' + filename
    response.content_type = file_mime_type(file_path)
    return response