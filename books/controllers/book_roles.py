from helper import Now
from ..models import BookRole
from uuid import uuid4


def add(db_session,data,username):

    model_instance = BookRole()
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    model_instance.tags = data.get('tags')
    model_instance.person_id = data.get('person_id')
    model_instance.book_id = data.get('book_id')
    model_instance.role = data.get('role')

    db_session.add(model_instance)

    return model_instance

def add_book_roles(book_id,roles_dict,db_session,username):
    result = []
    for role in roles_dict:
        data = {'role':role,
                'book_id':book_id,
                'person_id':roles_dict[role]}
        book_role = add(db_session,data,username)
        result.append(book_role)

    return result

def get(db_session,id):
    pass

def delete(db_session,id,username):
    pass
def get_all(db_session,id):
    pass
def edit(db_session,id,username):
    pass

