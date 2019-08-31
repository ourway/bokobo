from sqlalchemy import and_

from constraint_handler.models import UniqueEntityConnector
from log import logger, LogMsg
from helper import populate_basic_data, Http_error, Http_response
from messages import Message


def add(entity_id, unique_code, db_session):
    logger.info(LogMsg.START)

    try:
        model_instance = get(unique_code, db_session)
        if model_instance:
            logger.error(LogMsg.UNIQUE_CONSTRAINT_EXISTS,
                         {'entity_id': model_instance.entity_id,
                          'constraint_code': unique_code})
            raise Http_error(409, Message.ALREADY_EXISTS)

        model_instance = UniqueEntityConnector()
        populate_basic_data(model_instance, None, None)
        model_instance.UniqueCode = unique_code
        model_instance.entity_id = entity_id

        db_session.add(model_instance)
    except:
        logger.exception(LogMsg.UNIQUE_CONSTRAINT_EXISTS,exc_info=True)
        raise Http_error(409,Message.ALREADY_EXISTS)
    logger.info(LogMsg.END)
    return model_instance


def get(unique_code, db_session):
    logger.info(LogMsg.START)
    result = db_session.query(UniqueEntityConnector).filter(
        UniqueEntityConnector.UniqueCode == unique_code).first()
    return result


def delete(entity_id, db_session):
    logger.info(LogMsg.START)
    db_session.query(UniqueEntityConnector).filter(
        UniqueEntityConnector.entity_id == entity_id).delete()
    return Http_response(204,True)

def get_by_entity(entity_id,db_session):
    logger.info(LogMsg.START)
    result = db_session.query(UniqueEntityConnector).filter(
        UniqueEntityConnector.entity_id ==entity_id).first()
    return result