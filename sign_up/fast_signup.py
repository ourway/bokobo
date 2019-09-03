import json

from configs import SIGNUP_USER
from helper import Http_error, model_to_dict, check_schema
from log import logger, LogMsg
from app_redis import app_redis as redis
from messages import Message
from repository.user_repo import check_by_id
from send_message.send_message import send_message

from user.controllers.user import add as add_user, user_to_dict
from user.controllers.person import add as add_person


def signup(data, db_session, *args, **kwargs):
    logger.info(LogMsg.START, data)
    check_schema(['cell_no','signup_token','username','password'])
    logger.debug(LogMsg.SCHEMA_CHECKED)

    cell_no = data.get('cell_no')
    logger.debug(LogMsg.SIGNUP_GETTING_TOKEN_FROM_REDIS, cell_no)
    signup_token = redis.get(cell_no)
    if signup_token is None:
        logger.error(LogMsg.SIGNUP_TOKEN_NOT_IN_REDIS, cell_no)
        raise Http_error(404, Message.SIGNUP_TOKEN_NOT_EXISTS)

    signup_token = json.loads(signup_token.decode("utf-8")).get('signup_token',
                                                                None)
    if (signup_token is None) or (signup_token != data.get('signup_token')):
        logger.error(LogMsg.SIGNUP_TOKEN_INVALID,
                     {'redis_signup_token': signup_token,
                      'data_token': data.get('signup_token')})
        raise Http_error(404, Message.INVALID_SIGNUP_TOKEN)

    user_data = {k: v for k, v in data.items() if k in ['username', 'password']}
    person_data = {k: v for k, v in data.items() if k not in user_data.keys()}

    logger.debug(LogMsg.PERSON_GENERATING,person_data)
    person = add_person(db_session, person_data, SIGNUP_USER)

    if user_data:
        user_data.update({'person_id': person.id})
    logger.debug(LogMsg.USER_GENERATING,user_data)
    user = add_user(db_session, user_data, SIGNUP_USER)

    full_name = '{} {}'.format(data.get('last_name', ''), data.get('name', ''))

    user_welcoming_data = {'receptor': cell_no,
                           'message': ' {} به سرویس کتابخوان جام جم خوش آمدید.\n\n لحظات خوش مطالعه به سبک مدرن '.format(
                               full_name)}
    send_message(user_welcoming_data)
    logger.debug(LogMsg.SMS_SENT,user_welcoming_data)

    result = {'user': user_to_dict(user), 'person': model_to_dict(person)}
    logger.debug(LogMsg.SIGNUP_SUCCESS,result)
    logger.info(LogMsg.END)
    return result
