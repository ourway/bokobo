from constraint_handler.models import ConstraintHandler
from log import logger, LogMsg
from helper import populate_basic_data, Http_error, Http_response
from messages import Message

def add(data, db_session):
    logger.info(LogMsg.START)

    logger.debug(LogMsg.GENERATE_UNIQUE_CONSTRAINT, data)

    name = data.get('name')
    last_name = data.get('last_name')
    cell_no = data.get('cell_no')

    try:
        unique_code = ConstraintHandler()
        populate_basic_data(unique_code, 'INTERNAL', None)

        the_code = 'PERSON-{}-{}-{}'.format(name, last_name, cell_no)
        unique_code.UniqueCode = the_code

        logger.debug(LogMsg.UNIQUE_CONSTRAINT_IS, the_code)

        db_session.add(unique_code)
    except:
        logger.exception(LogMsg.UNIQUE_CONSTRAINT_EXISTS,exc_info=True)
        raise Http_error(409,Message.ALREADY_EXISTS)

    logger.info(LogMsg.END)

    return unique_code
