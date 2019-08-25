from constraint_handler.models import ConstraintHandler
from log import logger, LogMsg
from helper import populate_basic_data


def book_unique_code(book_data,db_session):
    logger.info(LogMsg.START)

    logger.debug(LogMsg.GENERATE_UNIQUE_CONSTRAINT,book_data)

    title = book_data.get('title',None)
    edition = book_data.get('edition',None)
    pub_year = book_data.get('pub_year',None)
    language = book_data.get('language',None)
    roles = book_data.get('roles',None)
    for item in roles:
        role_code =''



    unique_code = ConstraintHandler()
    populate_basic_data(unique_code,None,None)

    the_code = '{}-{}-{}-{}-{}'.format(title,pub_year,edition,language,role_code)

    unique_code.UniqueCode= the_code

    db_session.add(unique_code)


    return unique_code
