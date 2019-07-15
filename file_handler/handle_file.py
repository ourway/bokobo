import os
from uuid import uuid4

import magic
from bottle import response, static_file

from helper import value

save_path = value('save_path',None)


def upload_files(data, **kwargs):
    files_list = data.get('files')
    model_files  =[]
    if files_list and len(files_list) > 0:
        for file in files_list:
            if file:
                file.filename = str(uuid4())
                file_path = save_path+'/'+file.filename
                model_files.append(file_path)

            file.save(save_path)

    return model_files


def delete_files(files, **kwargs):

    for file in files:

        os.remove(file)


def return_file(file_path, **kwargs):
    filename = file_path.split('/')[-1]
    response.body = static_file(filename, root=save_path)
    response.content_type = file_mime_type(filename)
    return response


def file_mime_type(filename):
    # m = magic.open(magic.MAGIC_MIME)
    m = magic.from_file(filename, mime=True)
    print(m)

    return str(m)