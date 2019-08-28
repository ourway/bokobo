from uuid import uuid4
from sqlalchemy import and_
from follow.models import Follow
from helper import Http_error, Now, model_to_dict,check_schema
from log import LogMsg,logger
from messages import Message
from repository.person_repo import validate_person
from repository.user_repo import check_user


def add(db_session, data, username):
    logger.info(LogMsg.START,username)

    check_schema(['following_id'],data.keys())
    logger.debug(LogMsg.SCHEMA_CHECKED)
    following_id = data.get('following_id')

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    validate_person(following_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    if following_id == user.person_id:
        logger.error(LogMsg.FOLLOW_SELF_DENIED)
        raise Http_error(400, Message.FOLLOW_DENIED)

    logger.debug(LogMsg.FOLLOW_CHECK,data)
    follow = get(user.person_id, following_id, db_session)
    if follow is not None:
        logger.error(LogMsg.FOLLOW_EXISTS,data)
        raise Http_error(409, Message.ALREADY_FOLLOWS)

    model_instance = Follow()
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1
    model_instance.tags = data.get('tags')

    model_instance.following_id = following_id
    model_instance.follower_id = user.person_id

    db_session.add(model_instance)
    logger.debug(LogMsg.FOLLOW_ADD,follow_to_dict(model_instance))
    logger.info(LogMsg.END)

    return model_instance


def get_following_list(username, db_session):
    logger.info(LogMsg.START,username)

    result = []

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        logger.error(LogMsg.USER_HAS_NO_PERSON,username)
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)
    logger.debug(LogMsg.PERSON_EXISTS)

    res = db_session.query(Follow).filter(Follow.follower_id == user.person_id).all()
    for item in res:
        result.append(follow_to_dict(item))
    logger.debug(LogMsg.FOLLOWING_LIST,result)
    logger.info(LogMsg.END)

    return result


def get_follower_list(username, db_session):
    logger.info(LogMsg.START,username)

    result = []

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)

    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    validate_person(user.person_id, db_session)

    res = db_session.query(Follow).filter(Follow.following_id == user.person_id).all()
    for item in res:
        result.append(follow_to_dict(item))
    logger.debug(LogMsg.FOLLOWER_LIST,result)
    logger.info(LogMsg.END)

    return result


def delete(id, db_session, username, **kwargs):
    logger.info(LogMsg.START,username)

    user = check_user(username, db_session)
    if user is None:
        raise Http_error(400, Message.INVALID_USER)
    if user.person_id is None:
        raise Http_error(400, Message.Invalid_persons)

    model_instance = db_session.query(Follow).filter(
        and_(Follow.following_id == id, Follow.follower_id == user.person_id)).first()
    if model_instance:
        logger.debug(LogMsg.MODEL_GETTING)
    else:
        logger.debug(LogMsg.MODEL_GETTING_FAILED)
        raise Http_error(404, Message.NOT_FOUND)

    if model_instance.follower_id != user.person_id and \
            model_instance.following_id != user.person_id:
        raise Http_error(403, Message.ACCESS_DENIED)

    try:
        db_session.query(Follow).filter(and_(Follow.following_id == id, Follow.follower_id == user.person_id)).delete()
    except:
        raise Http_error(404, Message.DELETE_FAILED)
    logger.info(LogMsg.END)

    return {}


def follow_to_dict(follow_item):
    result = {
        'creation_date': follow_item.creation_date,
        'creator': follow_item.creator,
        'id': follow_item.id,
        'modification_date': follow_item.modification_date,
        'modifier': follow_item.modifier,
        'follower_id': follow_item.follower_id,
        'following_id': follow_item.following_id,
        'version': follow_item.version,
        'tags': follow_item.tags,
        'follower': model_to_dict(follow_item.follower),
        'following': model_to_dict(follow_item.following)
    }
    logger.info(LogMsg.END)
    return result


def get(follower_id, following_id, db_session):
    logger.info(LogMsg.START)

    return db_session.query(Follow).filter(
        and_(Follow.following_id == following_id, Follow.follower_id == follower_id)).first()


def get_following_list_internal(person_id, db_session):
    logger.info(LogMsg.START)

    result = []
    res = db_session.query(Follow).filter(Follow.follower_id == person_id).all()
    for item in res:
        result.append(item.following_id)
    logger.info(LogMsg.END)
    return result
