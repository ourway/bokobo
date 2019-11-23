from constraint_handler.models import ConstraintHandler
from helper import Http_response
from log import logger, LogMsg


def get(code, db_session):
    logger.debug(LogMsg.CHECK_UNIQUE_EXISTANCE,code)
    result =  db_session.query(ConstraintHandler).filter(
        ConstraintHandler.UniqueCode == code).first()
    if result is not None:
        logger.debug(LogMsg.UNIQUE_CONSTRAINT_EXISTS,code)
    else:
        logger.debug(LogMsg.UNIQUE_NOT_EXISTS,code)
    return result


def delete(code,db_session):
    logger.info(LogMsg.START)
    db_session.query(ConstraintHandler).filter(
        ConstraintHandler.UniqueCode == code).delete()
    logger.info(LogMsg.END)
    return Http_response(204,True)