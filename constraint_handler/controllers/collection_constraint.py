from constraint_handler.models import ConstraintHandler
from log import logger, LogMsg
from helper import populate_basic_data, Http_error, Http_response
from messages import Message
from .common_methods import get



def add(data, db_session):
    logger.info(LogMsg.START)

    logger.debug(LogMsg.GENERATE_UNIQUE_CONSTRAINT, data)

    title = data.get('title')
    person_id = data.get('person_id')

    try:
        unique_code = ConstraintHandler()
        populate_basic_data(unique_code, 'INTERNAL', None)

        the_code = 'COLLECTION-{}-{}'.format(title, person_id)
        unique_code.UniqueCode = the_code

        logger.debug(LogMsg.UNIQUE_CONSTRAINT_IS, the_code)

        db_session.add(unique_code)
    except:
        logger.exception(LogMsg.UNIQUE_CONSTRAINT_EXISTS,exc_info=True)
        raise Http_error(409,Message.ALREADY_EXISTS)

    logger.info(LogMsg.END)

    return unique_code

def unique_code_exists(data, db_session):
    logger.info(LogMsg.START)
    unique_code = generate_unique_code(data)

    unique = get(unique_code,db_session)

    return unique


def generate_unique_code(data):
    logger.info(LogMsg.START)

    logger.debug(LogMsg.GENERATE_UNIQUE_CONSTRAINT, data)

    title = data.get('title')
    person_id = data.get('person_id')
    the_code = 'COLLECTION-{}-{}'.format(title, person_id)
    return the_code