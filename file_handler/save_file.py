import os
from uuid import uuid4

from helper import value

save_path = value('save_path',None)


def upload_files(data,username):
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


def delete_files(data,username):
    files = data.get('files')
    for file in files:

        os.remove(file)
