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
                model_files.append(file.filename)

                file.save(save_path)

    return model_files


def delete_files(files, **kwargs):

    for filename in files:
        file_path = '{}/{}'.format(save_path,filename)

        os.remove(file_path)


def return_file(filename, **kwargs):
    response.body = static_file(filename, root=save_path)
    file_path = '{}/{}'.format(save_path,filename)
    response.content_type = file_mime_type(file_path)
    return response


def file_mime_type(filename):
    # m = magic.open(magic.MAGIC_MIME)
    m = magic.from_file(filename, mime=True)
    print(m)

    return str(m)