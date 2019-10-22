from helper import Http_error, populate_basic_data, edit_basic_data, Now, \
    model_to_dict
from log import LogMsg, logger
from messages import Message
from messaging.models import LastSeen
from repository.discussion_group_repo import is_group_member


def add(db_session, data):
    logger.info(LogMsg.START, '--INTERNAL--')

    logger.debug(LogMsg.SCHEMA_CHECKED)

    seen = get_internal(data.get('receptor_id'), data.get('sender_id'),
                        data.get('group_id'), db_session)
    if seen is not None:
        seen.last_seen = data.get('last_seen')
        edit_basic_data(seen, 'INTERNAL')
        logger.debug(LogMsg.LAST_SEEN_UPDATE,data)
        return seen

    model_instance = LastSeen()
    logger.debug(LogMsg.POPULATING_BASIC_DATA)
    populate_basic_data(model_instance, 'INTERNAL', data.get('tags'))
    model_instance.sender_id = data.get('sender_id')
    model_instance.receptor_id = data.get('receptor_id')
    model_instance.group_id = data.get('group_id', None)
    model_instance.last_seen = data.get('last_seen')

    db_session.add(model_instance)
    logger.debug(LogMsg.LAST_SEEN_ADD,data)
    logger.info(LogMsg.END)

    return model_instance


def get(id, db_session):
    logger.info(LogMsg.START)
    result = None
    try:
        logger.debug(LogMsg.MODEL_GETTING, id)
        result = db_session.query(LastSeen).filter(
            LastSeen.id == id).first()

    except:
        logger.exception(LogMsg.GET_FAILED, exc_info=True)
        Http_error(404, Message.NOT_FOUND)

    logger.info(LogMsg.END)
    return result


def get_by_receptor(receptor_id, db_session):
    groups = db_session.query(LastSeen).filter(
        LastSeen.receptor_id == receptor_id, LastSeen.group_id != None).all()
    directs = db_session.query(LastSeen).filter(
        LastSeen.receptor_id == receptor_id, LastSeen.group_id == None).all()
    return {'groups': groups, 'directs': directs}


def get_internal(receptor_id, sender_id, group_id, db_session):
    return db_session.query(LastSeen).filter(
        LastSeen.receptor_id == receptor_id, LastSeen.group_id == group_id,
        LastSeen.sender_id == sender_id).first()


def get_receptor_group_last_seen(receptor_id, group_id, db_session):
    return db_session.query(LastSeen).filter(
        LastSeen.receptor_id == receptor_id,
        LastSeen.group_id == group_id).first()


def get_receptor_sender_last_seen(receptor_id, sender_id, db_session):
    return db_session.query(LastSeen).filter(
        LastSeen.receptor_id == receptor_id,
        LastSeen.sender_id == sender_id).first()


def update_last_seen(message, person_id, db_session):
    logger.info(LogMsg.START)
    last_seen = None
    if message.receptor_id == person_id or (
            message.group_id is not None and is_group_member(person_id,
                                                             message.group_id,
                                                             db_session)):
        data = model_to_dict(message)
        data.update({'last_seen': Now()})
        logger.debug(LogMsg.LAST_SEEN_UPDATE,data)
        last_seen = add(db_session, data)
    logger.info(LogMsg.END)
    return last_seen

