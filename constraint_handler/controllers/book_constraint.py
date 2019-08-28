from constraint_handler.models import ConstraintHandler
from log import logger, LogMsg
from helper import populate_basic_data, Http_error, Http_response
from messages import Message
from .common_methods import get


def add(book_data, db_session):
    logger.info(LogMsg.START)

    logger.debug(LogMsg.GENERATE_UNIQUE_CONSTRAINT, book_data)

    title = book_data.get('title', None)
    edition = book_data.get('edition', None)
    pub_year = book_data.get('pub_year', None)
    language = book_data.get('language', None)
    roles = book_data.get('roles', None)
    type = book_data.get('type', None)
    role_codes = []
    for item in roles:
        role = item.get('role')
        person = item.get('person')
        person_id = person.get('id')
        if role is None or person_id is None:
            logger.error(LogMsg.DATA_MISSING,
                         {'role': role, 'person_id': person_id})
            raise Http_error(400, Message.MISSING_REQUIERED_FIELD)

        role_code = '{}{}'.format(role, person_id)
        role_codes.append(role_code)
    role_codes.sort()
    roles_string = ''.join(role_codes)


    try:
        unique_code = ConstraintHandler()
        populate_basic_data(unique_code, 'INTERNAL', None)

        the_code = 'Book-{}-{}-{}-{}-{}-{}'.format(str(title), str(pub_year), str(edition),
                                                str(language),str(type), roles_string)
        unique_code.UniqueCode = the_code

        logger.debug(LogMsg.UNIQUE_CONSTRAINT_IS, the_code)

        db_session.add(unique_code)
    except:
        logger.exception(LogMsg.UNIQUE_CONSTRAINT_EXISTS,exc_info=True)
        raise Http_error(409,Message.ALREADY_EXISTS)

    logger.info(LogMsg.END)

    return unique_code

def book_is_unique(code,db_session):
    res = get(code,db_session)
    if res is None:
        return True
    return False