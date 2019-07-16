import os
from uuid import uuid4

import magic
from bottle import response, static_file

from helper import value, Http_error
from messages import Message

save_path = value('save_path',None)


def upload_files(data, **kwargs):
    try:
        files_list = data.get('files')
        model_files  =[]
        if files_list and len(files_list) > 0:
            for file in files_list:
                if file:
                    file.filename = str(uuid4())
                    model_files.append(file.filename)

                    file.save(save_path)

        return model_files
    except:
        raise Http_error(405,Message.UPLOAD_FAILED)



def delete_files(files, **kwargs):
    try:
        for filename in files:
            file_path = '{}/{}'.format(save_path,filename)

            os.remove(file_path)
    except:
        raise Http_error(404,Message.MSG20)



def return_file(filename, **kwargs):
    try:

        response.body = static_file(filename, root=save_path)
        file_path = '{}/{}'.format(save_path,filename)
        response.content_type = file_mime_type(file_path)
        return response
    except:
        raise Http_error(404,Message.MSG20)



def file_mime_type(filename):
    # m = magic.open(magic.MAGIC_MIME)
    m = magic.from_file(filename, mime=True)
    return str(m)