import logging

from book_library.models import Library
from helper import check_schema, populate_basic_data
from log import LogMsg


def add(data,db_session):
    logging.info(LogMsg.START)

    check_schema(['book_id','person_id'], data.keys())

    model_instance = Library()

    populate_basic_data(model_instance)
    model_instance.person_id = data.get('person_id')
    model_instance.book_id = data.get('book_id')
    model_instance.status = {'status':'buyed','reading_started':False}

    db_session.add(model_instance)
    return model_instance

def add_books_to_library(person_id,book_list,db_session):
    result = []
    for book_id in book_list:
        lib_data = {'person_id':person_id,'book_id':book_id}

        result.append(add(lib_data,db_session))
    return result