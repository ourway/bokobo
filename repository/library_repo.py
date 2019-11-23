from books.controllers.book import book_to_dict
from helper import model_basic_dict


def library_to_dict(library,db_session):
    result =[]
    for item in library:
        lib_item = model_basic_dict(item)
        lib_attrs = {'status':item.status,
                     'book':book_to_dict(db_session,item.book)
                     }
        lib_item.update(lib_attrs)
        result.append(lib_item)
    return result

